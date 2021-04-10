from flask import render_template, redirect, url_for, jsonify, request, flash
from app import app
from app import ddb_handler as db_handler
from flask_login import current_user
import json
import os
import tempfile
import uuid
import boto3
from wand.image import Image

AWS_S3_DOMAIN = "https://a1db.s3.amazonaws.com/"
AWS_S3_BUCKET = "a1db"


'''
show the current loged in user profile
'''
@app.route('/', methods=['GET', 'POST'])
def main():
    if current_user.is_anonymous:
        return render_template("home.html")
    else:
        user = db_handler.get_user_by_name(current_user.username)
        user_posts = db_handler.get_posts_by_name(current_user.username)
        return render_template("profile.html", title="My Profile", user=user[0], posts=user_posts)


@app.route('/others_profile', methods=['GET', 'POST'])
def others_profile():
    print("others_profile")
    u = request.form['user_to_view']
    print(u)
    user = db_handler.get_user_by_name(u)
    user_posts = db_handler.get_posts_by_name(u)
    print(user[0]['userposts'])
    friendship = False
    if current_user.username in user[0]['followers']:
        friendship= True
        print("true")
    else:
        friendship= False
        print("false")
    return render_template("others_profile.html", title= "Others Profile", user=user[0], posts=user_posts, friend=friendship)



'''
show the current all feed from the followings
'''
@app.route('/index', methods=['GET', 'POST'])
def index():
    this_user = db_handler.get_user_by_name(current_user.username)
    all_followings_posts= {}
    all_followings ={}
    post_time={}
    for username in this_user[0]['following']:
        #following_user will have all user info from db
        following_user = db_handler.get_user_by_name(username)
        following_post={}
        if following_user:
            all_followings[username] = following_user[0]
            # follwing post will have all posts of a user
            following_post = db_handler.get_posts_by_name(username)
            for post in following_post:
                time_diff = int (db_handler.get_timedelta_minute(post['posttime']))
                time_order = time_diff
                if time_diff < 60:
                    time_diff = str(time_diff) + " min"
                elif time_diff >= 60 and time_diff <=1440:
                    time_diff = str(int (time_diff / 60)) + " hr"
                else:
                    time_diff = str(int (time_diff / 1440 )) + " day"
                post_time[post['postid']]= time_diff
                if following_post:
                    all_followings_posts[time_order] = {username: post}
        sorted_dict={}
        sorted_time = sorted(all_followings_posts)
        for time in sorted_time:
            sorted_dict[time] = all_followings_posts[time]
    return render_template("index.html", title="Feed", users=all_followings, posts=sorted_dict, this_user=this_user[0], post_time=post_time)


def update_likes(post_id):
    filename = os.path.join(app.static_folder, 'current_user.json')
    print("in update likes")
    with open(filename, "r+") as json_file:
        all_posts = json.load(json_file)
        for p in all_posts['posts']:
            if p['post_id'] == post_id:
                print("found")
                p['likes'] = p['likes']+1
        redirect(url_for('index'))

'''
the follow and unfollow function are used for jquery in all_user tab only
'''
@app.route('/follow', methods=['GET', 'POST'])
def follow():
    print("follow")
    filename = os.path.join(app.static_folder, 'current_user.json')
    user_to_follow = request.args.get('user_to_follow')
    u = request.args.get('u')
    print(user_to_follow)
    db_handler.put_user_following(u, user_to_follow)
    return jsonify(result="True")


@app.route('/unfollow', methods=['GET', 'POST'])
def unfollow():
    print("unfollow")
    user_to_unfollow = request.args.get('user_to_unfollow')
    u = request.args.get('u')
    print(user_to_unfollow)
    db_handler.put_user_unfollowing(u, user_to_unfollow)
    return jsonify(result="True")


'''
below profile_follow and profile_unfollow are used for click in profile page
'''
@app.route('/profile_follow', methods=['GET', 'POST'])
def profile_follow():
    print("profile_follow")
    user_to_follow = request.form['follow']
    print("user to follow: " + user_to_follow)
    u = request.form['current_user']
    db_handler.put_user_following(u, user_to_follow)
    call_back=db_handler.get_user_by_name(user_to_follow)
    print("call_back username : " + call_back[0]['username'])
    user_posts = db_handler.get_posts_by_name(user_to_follow)
    return render_template("others_profile.html",title = "Others Profile", user=call_back[0], posts=user_posts, friend=True)


@app.route('/profile_unfollow', methods=['GET', 'POST'])
def profile_unfollow():
    print("profile_unfollow")
    user_to_unfollow = request.form['unfollow']
    u = request.form['current_user']
    print("user to unfollow: " + user_to_unfollow)
    db_handler.put_user_unfollowing(u, user_to_unfollow)
    call_back = db_handler.get_user_by_name(user_to_unfollow)
    print("call_back username : " + call_back[0]['username'])
    user_posts = db_handler.get_posts_by_name(user_to_unfollow)
    return render_template("others_profile.html", title= "Others Profile", user=call_back[0], posts=user_posts, friend=False)


'''
change the profile picture
'''
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    print("edit_profile")
    return render_template("upload_profile_pic.html", title= "Edit My Profile")


@app.route('/change_profile_bio', methods=['GET', 'POST'])
def change_profile_bio():
    # need to change the bio for current user in the db
    return redirect(url_for('index'))


@app.route('/followers', methods=['GET', 'POST'])
def followers():
    cur_user = request.form['user_to_view_followers']
    this_user = db_handler.get_user_by_name(cur_user)
    all_users = {}
    for username in this_user[0]['followers']:
        followers_info = db_handler.get_user_by_name(username)
        if followers_info:
            all_users[username] = followers_info[0]
    return render_template("followers.html", title="Followers", user=this_user[0], all_users=all_users)


@app.route('/followings', methods=['GET', 'POST'])
def followings():
    cur_user = request.form['user_to_view_followings']
    this_user = db_handler.get_user_by_name(cur_user)
    all_users = {}
    for username in this_user[0]['following']:
        followings_info = db_handler.get_user_by_name(username)
        if followings_info:
            all_users[username] = followings_info[0]
    return render_template("followings.html", title="Followings", user=this_user[0], all_users=all_users)


'''
for current user to send new post
'''
@app.route('/new_post', methods=['GET', 'POST'])
def send_new_post():
    # need to change the bio for current user in the db
    if request.method == 'POST':
        image_file = request.files['upload_image']
        image_text = request.form['upload_text']

        if image_file.filename == '':
            flash('Empty image', 'danger')
            return render_template("send_new_post.html", title="New Post")

        file_handle, path = tempfile.mkstemp()
        filename_original = path+"_original.jpeg"
        with Image(file=image_file) as img:
            img.save(filename=filename_original)
        s3_image_key = str(uuid.uuid4())+".png"
        s3_image_data = open(filename_original, "rb").read()
        s3_cli = boto3.client('s3', region_name='us-east-1')
        s3_cli.put_object(Bucket=AWS_S3_BUCKET, Key=s3_image_key, Body=s3_image_data, ACL='public-read')

        db_handler.put_post(current_user.username, AWS_S3_DOMAIN+s3_image_key, image_text)

        os.remove(path)
        os.remove(filename_original)
        return redirect(url_for('main'))
    else:
        return render_template("send_new_post.html", title="New Post")


@app.route('/all_user', methods=['GET', 'POST'])
def all_user():
    all_users = db_handler.get_all_users()
    friendship ={}
    for user in all_users:
        if user['username'] != current_user.username:
            this_user = db_handler.get_user_by_name(user['username'])
            print(this_user[0]['followers'])
            if current_user.username in this_user[0]['followers']:
                friendship[user['username']] = True
                print(user['username'] + "true")
            else:
                friendship[user['username']] = False
                print(user['username'] + "false")
    return render_template("all_user.html", title="All Register users", user=all_users, friendship=friendship)


'''
update the actual profile picture
'''
@app.route('/upload_profile_pic', methods=['GET', 'POST'])
def upload_profile_pic():
    if request.method == 'POST':
        image_file = request.files['upload_profile']
        if image_file.filename == '':
            flash('Empty profile image', 'danger')
            return render_template("upload_profile_pic.html", title="Upload Profile Picture")
        file_handle, path = tempfile.mkstemp()
        filename_original = path+"_original.jpeg"
        with Image(file=image_file) as img:
            img.save(filename=filename_original)

        s3_image_key = str(uuid.uuid4())+".png"
        s3_image_data = open(filename_original, "rb").read()
        s3_cli = boto3.client('s3', region_name='us-east-1')
        s3_cli.put_object(Bucket=AWS_S3_BUCKET, Key=s3_image_key, Body=s3_image_data, ACL='public-read')

        db_handler.put_user_info(current_user.username, _img=AWS_S3_DOMAIN+s3_image_key)
        os.remove(path)
        os.remove(filename_original)
        return redirect(url_for('main'))

    else:
        return render_template("upload_profile_pic.html", title="Upload Profile Picture")

'''
post new comment by followers
'''
@app.route('/post_comment', methods=['GET', 'POST'])
def post_comment():
    print("post_comment")
    cur_user = request.args.get('cur_user')
    postid = request.args.get('postid')
    comment = request.args.get('comment')
    db_handler.put_post_comment(cur_user, postid, comment)
    return jsonify(result="True")


@app.route('/view_comments', methods=['GET', 'POST'])
def view_comments():
    print("view_comments")
    post_id= request.form['post_id']
    post_info = db_handler.get_post_by_postid(post_id)
    return render_template("view_comments.html", title="view comments", post=post_info[0])
