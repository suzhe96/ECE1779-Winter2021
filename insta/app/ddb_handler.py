from __future__ import print_function # Python 2/3 compatibility
import boto3
import json

from boto3.dynamodb.conditions import Key, Attr
import pdb

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


'''
RETURN FORMAT
[
    {
        'profile_img': 'https://a1db.s3.amazonaws.com/mike_profile.jpeg',
        'username': 'Mike',
        'userposts': [],
        'loc': 'Beijing',
        'bio': 'Today is good'
    },
    {
        'profile_img': 'https://a1db.s3.amazonaws.com/david_profile.jpeg',
        'username': 'David',
        'userposts': [Decimal('1'), Decimal('2')],
        'loc': 'Toronto',
        'bio': 'Today is good'
    }
]
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


'''
RETURN FORMAT
[
    {
        'img': 'https://a1db.s3.amazonaws.com/david_post1.jpeg',
        'likes': Decimal('10'),
        'commentContent': ['Nice Post', 'wow'],
        'commentOwner': ['Mike', 'Mike'],
        'postid': Decimal('1'),
        'posttime': 'timestamp',
        'postowner': 'David'
    },
    {
        'img': 'https://a1db.s3.amazonaws.com/david_post2.jpeg',
        'likes': Decimal('5'),
        'commentContent': ['What a post!'],
        'commentOwner': ['Mike'],
        'postid': Decimal('2'),
        'posttime': 'timestamp',
        'postowner': 'David'
    }
]
'''
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


'''
[
    {
        'following': ['Terry', 'Mike'],
        'profile_img': 'https://a1db.s3.amazonaws.com/david_profile.jpeg',
        'userposts': [Decimal('1'), Decimal('2')],
        'followers': ['Marry'],
        'bio': 'Today is good',
        'username': 'David',
        'loc': 'Toronto'
    }
]
'''
def get_user_by_name(username):
    records = []
    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    for i in response['Items']:
        records.append(i)
    
    return records


'''
A(username) follows B(username)
'''
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


'''
A(username) unfollows B(username)
'''
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

