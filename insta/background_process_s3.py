import boto3
import json
import uuid

from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
import pdb

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def lambda_handler(event, context):
    # 86400 seconds (10 days is the threshold for zombie users)
    posttime = get_utc_time()
    threshold = int(posttime) - 864000
    records = get_all()
    print("S3 LAMBDA GET RECORDS: {}".format(records))
    for record in records:
        lastlogin = record['lastlogin']
        if int(lastlogin) > threshold:
            continue
        delete_posts(record['userposts'], record['username'])
        delete_user(record['username'])
        

def delete_posts(posts, username):
    table = dynamodb.Table('Posts')
    for postid in posts:
        _ = table.delete_item(
            Key={
                'postid': postid,
                'postowner': username
            }
        ) 


def delete_user(username):
    table = dynamodb.Table('Users')
    _ = table.delete_item(
        Key={
            'username': username
        }
    ) 


def get_all():
    table = dynamodb.Table('Users')
    pe = "username, userposts, lastlogin"
    response = table.scan(
        ProjectionExpression=pe,
    )

    records = []

    for i in response['Items']:
        records.append(i)

    while 'LastEvaluatedKey' in response:
        response = table.scan(
            ProjectionExpression=pe,
            ExclusiveStartKey=response['LastEvaluatedKey']
            )
        for i in response['Items']:
            records.append(i)

    return records


def get_utc_time():
    dt = datetime.utcnow()
    posttime = str(dt.day * 24 * 60 * 60 + dt.hour * 60 * 60 + dt.minute * 60 + dt.second)
    return posttime
