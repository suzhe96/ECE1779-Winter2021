from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

from boto3.dynamodb.conditions import Key, Attr
import pdb

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def create_table():
    userTable = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'userid',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'name',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'userid',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    postTable = dynamodb.create_table(
        TableName='Posts',
        KeySchema=[
            {
                'AttributeName': 'postid',
                'KeyType': 'HASH'  #Partition key
            },
            {
                'AttributeName': 'owner',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'postid',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'owner',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def delete_table():
    response = dynamodb.delete_table(
        TableName='Users'
    )
    response = dynamodb.delete_table(
        TableName='Posts'
    )


def import_data():
    print("Import users...")
    table = dynamodb.Table('Users')
    with open("app/static/preset_users.json") as json_file:
        users = json.load(json_file)
        for user in users:
            userid = int(user['userid'])
            name = user['name']
            info = user['info']

            print("Adding user: {}".format(name))

            item = {
                'userid': userid,
                'name': name
            }
            item.update(info)

            table.put_item(
               Item = item
            )
    print("Finished import users...")

    print("Import posts")
    table = dynamodb.Table('Posts')
    with open("app/static/preset_posts.json") as json_file:
        posts = json.load(json_file)
        for post in posts:
            postid = int(post['postid'])
            owner = post['owner']
            info = post['info']

            print("Adding {}'s post: {}".format(owner, postid))

            item = {
                'postid': postid,
                'owner': owner
            }
            item.update(info)

            table.put_item(
               Item = item
            )
    print("Finished import posts")


if __name__ == "__main__":
    # create_table()
    import_data()