import mysql.connector
from flask import g
from app import a1_webapp
from app.dbconfig import *
import boto3, botocore


def connect_to_database_debug():
    return mysql.connector.connect(user=DATABASE_LOCAL_CONFIG['user'],
                                   password=DATABASE_LOCAL_CONFIG['password'],
                                   host=DATABASE_LOCAL_CONFIG['host'],
                                   database=DATABASE_LOCAL_CONFIG['db'])


def initialize_s3_handler():
    s3_client = boto3.client("s3",
                      aws_access_key_id=AWS_S3_CONFIG['aws_access_key'],
                      aws_secret_access_key=AWS_S3_CONFIG['aws_secret_access_key'])
    # s3_client.create_bucket(Bucket=AWS_S3_CONFIG['aws_bucket_name'])
    return s3_client


def get_db(Debug=False):
    db = getattr(g, '_database', None)
    if db is None:
        if Debug:
            db = g._database = connect_to_database_debug()
        else:
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
