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
                'AttributeName': 'username',
                'KeyType': 'HASH'  #Partition key
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
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
                'AttributeName': 'postowner',
                'KeyType': 'RANGE'  #Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'postid',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'postowner',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )


def delete_table():
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
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
            username = user['username']
            info = user['info']

            print("Adding user: {}".format(username))

            item = {
                'username': username
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
            postowner = post['postowner']
            info = post['info']

            print("Adding {}'s post: {}".format(postowner, postid))

            item = {
                'postid': postid,
                'postowner': postowner
            }
            item.update(info)

            table.put_item(
               Item = item
            )
    print("Finished import posts")



'''
################### TEST DDB_HANDLER ##################
'''
def get_all_users():
    table = dynamodb.Table('Users')
    pe = "username, profile_img, bio, loc, userposts"
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

def get_posts_by_name(username):
    # Get post id belonging to that user
    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    postid_list = response['Items'][0]['userposts']

    # Get all posts
    records = []
    table = dynamodb.Table('Posts')
    for postid in postid_list:
        response = table.query(
            KeyConditionExpression=Key('postid').eq(int(postid))
        )
        for i in response['Items']:
            records.append(i)

    return records

def get_user_by_name(username):
    records = []
    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    for i in response['Items']:
        records.append(i)
    
    return records

def put_user_following(A, B):
    table = dynamodb.Table('Users')
    # get A following list
    response = table.query(
            KeyConditionExpression=Key('username').eq(A)
        )
    A_following = response['Items'][0]['following']
    A_following.append(B)
    # get B follower list
    response = table.query(
            KeyConditionExpression=Key('username').eq(B)
        )
    B_follower = response['Items'][0]['followers']
    B_follower.append(A)
    # update A
    _ = table.update_item(
       Key={
            'username': A,
        },
        UpdateExpression = "set following = :f",
        ExpressionAttributeValues = {
           ':f': A_following
        }
    )

    # update B
    _ = table.update_item(
       Key={
            'username': B,
        },
        UpdateExpression = "set followers = :f",
        ExpressionAttributeValues = {
           ':f': B_follower
        }
    )

def put_user_unfollowing(A, B):
    table = dynamodb.Table('Users')
    # get A following list
    response = table.query(
            KeyConditionExpression=Key('username').eq(A)
        )
    A_following = response['Items'][0]['following']
    A_following.remove(B)

    # get B follower list
    response = table.query(
            KeyConditionExpression=Key('username').eq(B)
        )
    B_follower = response['Items'][0]['followers']
    B_follower.remove(A)

    # update A
    _ = table.update_item(
       Key={
            'username': A,
        },
        UpdateExpression = "set following = :f",
        ExpressionAttributeValues = {
           ':f': A_following
        }
    )

    # update B
    _ = table.update_item(
       Key={
            'username': B,
        },
        UpdateExpression = "set followers = :f",
        ExpressionAttributeValues = {
           ':f': B_follower
        }
    )

if __name__ == "__main__":
    # delete_table()
    # create_table()
    # import_data()
    # print(get_posts_by_name("David"))
    # print(get_user_by_name("David"))
    # print(get_all_users())
    # put_user_following("Mike", "David")
    # put_user_unfollowing("Mike", "David")

