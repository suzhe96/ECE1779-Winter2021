import requests
import json
import mysql.connector
from flask import g
from app import a1_webapp
from app.dbconfig import *
import boto3, botocore


def get_aws_credentials():
    if DEPLOY_BUILT:
        aws_response = requests.get(AWS_CREDENTIALS_REQUEST.format(AWS_S3_CONFIG['aws_iam_role']))
        aws_response_json = json.loads(aws_response.content.decode())
        return {"aws_access_key": aws_response_json['AccessKeyId'],
                "aws_secret_access_key": aws_response_json['SecretAccessKey'],
                "aws_session_token": aws_response_json['Token']}
    else:
        return AWS_CREDENTIALS_PERSONAL

# MySQL requires to be deployed locally (on the device where the applicatio is running)
def connect_to_database():
    return mysql.connector.connect(user=DATABASE_LOCAL_CONFIG['user'],
                                   password=DATABASE_LOCAL_CONFIG['password'],
                                   host=DATABASE_LOCAL_CONFIG['host'],
                                   database=DATABASE_LOCAL_CONFIG['db'])

# S3 handler from Xun's personal account if local built
# S3 handler from EC2 instance if deploy built
def initialize_s3_handler():
    aws_credentials = get_aws_credentials()
    s3_client = boto3.client("s3",
                      aws_access_key_id=aws_credentials['aws_access_key'],
                      aws_secret_access_key=aws_credentials['aws_secret_access_key'],
                      aws_session_token=aws_credentials['aws_session_token'])
    return s3_client


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

def get_s3():
    s3_client = getattr(g, '_s3_handler', None)
    if s3_client is None:
        s3_client = g._s3_handler = initialize_s3_handler()
    return s3_client


@a1_webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


s3 = boto3.client(
    "s3",
    aws_access_key_id='AWS_ACCESS_KEY',
    aws_secret_access_key='AWS_SECRET_ACCESS_KEY'
)

BUCKET_NAME = 'a1-db'
