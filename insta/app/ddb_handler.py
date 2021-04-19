from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import uuid

from datetime import datetime
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
        'postowner': 'David',
        'postcontent': 'This is wonderful world to live in!'
    }
]
'''
def get_posts_by_name(username):
    # Get post id belonging to that user
    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    postid_list = []
    if response['Items'][0]['userposts']:
        postid_list = response['Items'][0]['userposts']
    # Get all posts
    records = []
    table = dynamodb.Table('Posts')
    for postid in postid_list:
        response = table.query(
            KeyConditionExpression=Key('postid').eq(postid)
        )
        for i in response['Items']:
            records.append(i)

    return records



'''
Get post given postid
'''
def get_post_by_postid(postid):
    table = dynamodb.Table('Posts')
    records = []
    response = table.query(
            KeyConditionExpression=Key('postid').eq(postid)
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
        'userlikes': ['1']
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
Here the validation reply on caller, make sure A has not yet followed B
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
Here the validation reply on caller, make sure A has already followed B
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


'''
Like a post given by postid and username
Here the validation reply on caller, make sure postid existed
'''
def put_post_likes(postid, username):
    table = dynamodb.Table('Posts')

    # Get likes
    response = table.query(
            KeyConditionExpression=Key('postid').eq(postid)
        )
    likes = response['Items'][0]['likes']
    postowner = response['Items'][0]['postowner']
    likes += 1

    # Update Likes
    _ = table.update_item(
       Key={
            'postid': postid,
            'postowner': postowner
        },
        UpdateExpression = "set likes = :l",
        ExpressionAttributeValues = {
           ':l': likes
        }
    )

    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    userlikes = response['Items'][0]['userlikes']
    userlikes.append(postid)
    _ = table.update_item(
       Key={
            'username': username,
        },
        UpdateExpression = "set userlikes = :ul",
        ExpressionAttributeValues = {
           ':ul': userlikes,
        }
    )


'''
Unlike a post given by postid and username
Here the validation reply on caller, make sure postid existed
'''
def put_post_unlikes(postid, username):
    table = dynamodb.Table('Posts')

    # Get likes
    response = table.query(
            KeyConditionExpression=Key('postid').eq(postid)
        )
    likes = response['Items'][0]['likes']
    postowner = response['Items'][0]['postowner']
    likes -= 1

    # Update Likes
    _ = table.update_item(
       Key={
            'postid': postid,
            'postowner': postowner
        },
        UpdateExpression = "set likes = :l",
        ExpressionAttributeValues = {
           ':l': likes
        }
    )


    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    userlikes = response['Items'][0]['userlikes']
    userlikes.remove(postid)
    _ = table.update_item(
       Key={
            'username': username,
        },
        UpdateExpression = "set userlikes = :ul",
        ExpressionAttributeValues = {
           ':ul': userlikes,
        }
    )


'''
A(username) comments on a post given by postid and content
Here the validation reply on caller, make sure postid existed
'''
def put_post_comment(A, postid, content):
    table = dynamodb.Table('Posts')

    # Get commentOwner and commentContent
    response = table.query(
            KeyConditionExpression=Key('postid').eq(postid)
        )
    postowner = response['Items'][0]['postowner']
    commentOwner = response['Items'][0]['commentOwner']
    commentContent = response['Items'][0]['commentContent']
    commentOwner.append(A)
    commentContent.append(content)

    # Update comment
    _ = table.update_item(
       Key={
            'postid': postid,
            'postowner': postowner
        },
        UpdateExpression = "set commentOwner = :owner, commentContent = :content",
        ExpressionAttributeValues = {
           ':owner': commentOwner,
           ':content': commentContent
        }
    )


'''
A(username) posts new img(path to s3) with description
Here the validation reply on caller, make sure user A existed
'''
def put_post(A, img, description):
    # Update post
    table = dynamodb.Table('Posts')
    posttime = get_utc_time()
    postid = str(uuid.uuid1())
    _ = table.put_item(
       Item={
            'postid': postid,
            'postowner': A,
            'img': img,
            'likes': 0,
            'posttime': posttime,
            'postcontent': description,
            'commentOwner': [],
            'commentContent': []
        }
    )

    # Update userposts in users
    table = dynamodb.Table('Users')
    response = table.query(
            KeyConditionExpression=Key('username').eq(A)
        )
    userposts = response['Items'][0]['userposts']
    userposts.append(postid)

    _ = table.update_item(
       Key={
            'username': A,
        },
        UpdateExpression = "set userposts = :u",
        ExpressionAttributeValues = {
           ':u': userposts,
        }
    )


'''
New user A registered with blank profile img(path to s3), loc, bio
'''
def put_user(A, bio, loc):
    table = dynamodb.Table('Users')
    _ = table.put_item(
        Item = {
            'username': A,
            'profile_img': 'https://a1db.s3.amazonaws.com/blank_profile_pic.png',
            'userposts': [],
            'bio': bio,
            'loc': loc,
            'followers': [],
            'following': []
        }
    )


'''
update user info given username
'''
def put_user_info(username, _img=None, _bio=None, _loc=None):
    table = dynamodb.Table('Users')

    response = table.query(
            KeyConditionExpression=Key('username').eq(username)
        )
    profile_img = response['Items'][0]['profile_img']
    bio = response['Items'][0]['bio']
    loc = response['Items'][0]['loc']

    if _img is not None:
        profile_img = _img
    if _bio is not None:
        bio = _bio
    if _loc is not None:
        loc = _loc

    _ = table.update_item(
       Key={
            'username': username,
        },
        UpdateExpression = "set profile_img = :img, bio = :b, loc = :l",
        ExpressionAttributeValues = {
           ':img': profile_img,
           ':b': bio,
           ':l': loc
        }
    )


'''
update user last login time given username
'''
def put_user_logintime(username):
    table = dynamodb.Table('Users')
    posttime = get_utc_time()
    _ = table.update_item(
       Key={
            'username': username,
        },
        UpdateExpression = "set lastlogin = :login",
        ExpressionAttributeValues = {
           ':login': posttime,
        }
    )

'''
[
    {
        'actionTime': '2021-04-16 08:47:20.322396',
        'actionDescription': 'New user registered: David',
        'actionType': 'INSERT'
    },
    {
        'actionTime': '2021-04-16 08:48:20.322396',
        'actionDescription': 'New user registered: Mike',
        'actionType': 'INSERT'
    }
]
'''
def get_all_logs():
    table = dynamodb.Table('Logs')
    pe = "actionTime, actionType, actionDescription"
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
Helper: return timedelta in minutes given timestamp(str)
'''
def get_timedelta_minute(timestamp):
    dt = datetime.utcnow()
    curtime = dt.day * 24 * 60 * 60 + dt.hour * 60 * 60 + dt.minute * 60 + dt.second
    return  (curtime - int(timestamp)) / 60


'''
Helper: return utc time(str): only count until day
'''
def get_utc_time():
    dt = datetime.utcnow()
    posttime = str(dt.day * 24 * 60 * 60 + dt.hour * 60 * 60 + dt.minute * 60 + dt.second)
    return posttime