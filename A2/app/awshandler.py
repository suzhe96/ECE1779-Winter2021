import requests
import json
import mysql.connector
from flask import g
from app import a2 
from app.awsconfig import *
import boto3, botocore


session = None
elb = None
ec2 = None
ec2_resource = None
cloudwatch = None


def get_aws_credentials():
    aws_response = requests.get(AWS_CREDENTIALS_CONFIG['request'].format(AWS_CREDENTIALS_CONFIG['iam_role']))
    aws_response_json = json.loads(aws_response.content.decode())
    return {'aws_access_key' : aws_response_json['AccessKeyId'],
            'aws_secret_access_key' : aws_response_json['SecretAccessKey'],
            'aws_session_token' : aws_response_json['Token']}


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


def get_elb():
    # elb = getattr(g, '_boto3_elb', None)
    global session, elb
    if elb is None:
        session = get_boto3_session() 
        elb = session.client(AWS_GENERAL_CONFIG['elb_service'],
                             region_name=AWS_GENERAL_CONFIG['region'])
    return elb


def get_ec2():
    # ec2 = getattr(g, '_boto3_ec2', None)
    global session, ec2
    if ec2 is None:
        session = get_boto3_session() 
        ec2 = session.client(AWS_GENERAL_CONFIG['ec2_service'],
                             region_name=AWS_GENERAL_CONFIG['region'])
    return ec2

def get_ec2_resource():
    # ec2_resource = getattr(g, '_boto3_ec2_resource', None)
    global session, ec2_resource
    if ec2_resource is None:
        session = get_boto3_session() 
        ec2_resource = session.resource(AWS_GENERAL_CONFIG['ec2_service'])
    return ec2_resource


def get_cloudwatch():
    # cloudwatch = getattr(g, '_boto3_cloudwatch', None)
    global session, cloudwatch
    if cloudwatch is None:
        session = get_boto3_session() 
        cloudwatch = session.client(AWS_GENERAL_CONFIG['cloudwatch_service'])
    return cloudwatch

