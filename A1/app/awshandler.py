import requests
import json
import mysql.connector
from flask import g
from app import a1_webapp
from app.awsconfig import *
import boto3, botocore
from threading import Lock

session = None
s3_client = None
cloudwatch = None
http_request_count = 0


def get_aws_credentials():
    aws_response = requests.get(AWS_CREDENTIALS_CONFIG['request'].format(AWS_CREDENTIALS_CONFIG['iam_role']))
    aws_response_json = json.loads(aws_response.content.decode())
    return {'aws_access_key' : aws_response_json['AccessKeyId'],
            'aws_secret_access_key' : aws_response_json['SecretAccessKey'],
            'aws_session_token' : aws_response_json['Token']}


def get_instance_id():
    aws_response = requests.get(AWS_CREDENTIALS_CONFIG['request_inst_id'])
    return aws_response.content.decode()


def connect_to_database():
    return mysql.connector.connect(user=DATABASE_LOCAL_CONFIG['user'],
                                   password=DATABASE_LOCAL_CONFIG['password'],
                                   host=DATABASE_LOCAL_CONFIG['host'],
                                   database=DATABASE_LOCAL_CONFIG['db'])


def get_boto3_session():
    aws_credentials = get_aws_credentials()
    # session = getattr(g, '_boto3_session', None)
    global session
    if session is None:
        session = boto3.Session(aws_access_key_id=aws_credentials['aws_access_key'],
                                aws_secret_access_key=aws_credentials['aws_secret_access_key'],
                                aws_session_token=aws_credentials['aws_session_token'],
                                region_name=AWS_GENERAL_CONFIG['region'])
    return session


def initialize_cloudwatch_handler():
    aws_credentials = get_aws_credentials()



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

def get_s3():
    # s3_client = getattr(g, '_s3_handler', None)
    global session, s3_client
    if s3_client is None:
        session = get_boto3_session()
        s3_client = session.client(AWS_GENERAL_CONFIG['s3_service'])
    return s3_client

def get_cloudwatch():
    # cloudwatch = getattr(g, '_boto3_cloudwatch', None)
    global session, cloudwatch
    if cloudwatch is None:
        session = get_boto3_session() 
        cloudwatch = session.client(AWS_GENERAL_CONFIG['cloudwatch_service'])
    return cloudwatch


@a1_webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

