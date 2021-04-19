import boto3
import json
import uuid

from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
import pdb

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):

    ret = parse_records(event['Records'])

    for log in ret:
        put_log(log[0], log[1])


def put_log(actionType, content):
    table = dynamodb.Table('Logs')
    dt = datetime.utcnow()
    item = {
        'actionTime': str(dt),
        'actionType': actionType,
        'actionDescription': content
    }
    table.put_item(
        Item = item
    )


def parse_records(records):
    ret = []
    for record in records:
        # get actionType
        actionType = record['eventName']
        # table name
        table = record['eventSourceARN'].split("/")[1]
        # now only handle two actions: insert or modify
        # case insert:
        if actionType == "INSERT" and table == "Posts":
            postowner = record['dynamodb']['Keys']['postowner']['S']
            postid = record['dynamodb']['Keys']['postid']['S']
            content = "{} new post: postid = {}".format(postowner, postid)
            ret.append([actionType, content])
        if actionType == "INSERT" and table == "Users":
            username = record['dynamodb']['Keys']['username']['S']
            content = "new registered user {}".format(username)
            ret.append([actionType, content])
        # case modify:
        if actionType == "MODIFY" and table == "Posts":
            # we care about the new comment on the post
            postowner = record['dynamodb']['Keys']['postowner']['S']
            postid = record['dynamodb']['Keys']['postid']['S']
            newImageComment = record['dynamodb']['NewImage']
            oldImageComment = record['dynamodb']['OldImage']
            if len(newImageComment['commentOwner']['L']) > len(oldImageComment['commentOwner']['L']):
                commentOwner = newImageComment['commentOwner']['L'][-1]['S']
                commentContent = newImageComment['commentContent']['L'][-1]['S']
                content = "{} comment on {}'s post({}): {}".format(commentOwner, postowner, postid, commentContent)
                ret.append([actionType, content])
        if actionType == "MODIFY" and table == "Users":
            username = record['dynamodb']['Keys']['username']['S']
            newImage = record['dynamodb']['NewImage']
            oldImage = record['dynamodb']['OldImage']
            # case following
            if len(newImage['following']['L']) > len(oldImage['following']['L']):
                newfollowing = newImage['following']['L'][-1]['S']
                content = "{} is following {}".format(username, newfollowing)
                ret.append([actionType, content])

            if len(newImage['followers']['L']) > len(oldImage['followers']['L']):
                newfollower = newImage['followers']['L'][-1]['S']
                content = "{} has a new follower: {}".format(username, newfollower)
                ret.append([actionType, content])

            if len(newImage['following']['L']) < len(oldImage['following']['L']):
                oldfollowing = oldImage['following']['L'][-1]['S']
                content = "{} is unfollowing {}".format(username, oldfollowing)
                ret.append([actionType, content])

            if len(newImage['followers']['L']) < len(oldImage['followers']['L']):
                oldfollower = oldImage['followers']['L'][-1]['S']
                content = "{} has lost a follower: {}".format(username, oldfollower)
                ret.append([actionType, content])

            if newImage['bio'] != oldImage['bio']:
                newBio = newImage['bio']['S']
                content = "{} updates bio: {}".format(username, newBio)
                ret.append([actionType, content])
            
            if newImage['loc'] != oldImage['loc']:
                newLoc = newImage['loc']['S']
                content = "{} updates location: {}".format(username, newLoc)
                ret.append([actionType, content])

            if len(newImage['userlikes']['L']) > len(oldImage['userlikes']['L']):
                newlikes = newImage['userlikes']['L'][-1]['S']
                content = "{} likes the post {}".format(username, newlikes)
                ret.append([actionType, content])

            if len(newImage['userlikes']['L']) < len(oldImage['userlikes']['L']):
                oldlikes = oldImage['userlikes']['L'][-1]['S']
                content = "{} unlikes the post {}".format(username, oldlikes)
                ret.append([actionType, content])
        # case remove:
        if actionType == "REMOVE" and table == "Posts":
            oldImage = record['dynamodb']['OldImage']
            postowner = oldImage['postowner']['S']
            postid = oldImage['postid']['S']
            content = "{}'s post has been deleted: postid = {}".format(postowner, postid)
            ret.append([actionType, content])
        if actionType == "REMOVE" and table == "Users":
            username = record['dynamodb']['OldImage']['username']['S']
            content = "User {} has been deleted".format(username)
            ret.append([actionType, content])
    return ret
        


