from flask import render_template, redirect, url_for, jsonify, request
from app import app
from app import ddb_handler as db_handler
from flask_login import current_user
import json
import os


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
        return render_template("profile.html", user=user[0], posts=user_posts)


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
    return render_template("others_profile.html", user=user[0], posts=user_posts, friend=friendship)



'''
show the current all feed from the followings
'''
@app.route('/index', methods=['GET', 'POST'])
def index():
    #FIXME, need to get an dict of all followings of current user
    filename = os.path.join(app.static_folder, 'current_user.json')
    with open(filename) as json_file:
        user = json.load(json_file)
        return render_template("index.html", title="Feed", user=user)


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
    return render_template("others_profile.html", user=call_back[0], posts=user_posts, friend=True)


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
    return render_template("others_profile.html", user=call_back[0], posts=user_posts, friend=False)


'''
change the profile picture
'''
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    print("edit_profile")
    return render_template("upload_profile_pic.html")


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
    return render_template("followers.html", user=this_user[0], all_users=all_users)


@app.route('/followings', methods=['GET', 'POST'])
def followings():
    cur_user = request.form['user_to_view_followings']
    this_user = db_handler.get_user_by_name(cur_user)
    all_users = {}
    for username in this_user[0]['following']:
        followings_info = db_handler.get_user_by_name(username)
        if followings_info:
            all_users[username] = followings_info[0]
    return render_template("followings.html", user=this_user[0], all_users=all_users)


'''
for current user to send new post
'''
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    # need to change the bio for current user in the db
    return render_template("send_new_post.html")


@app.route('/all_user', methods=['GET', 'POST'])
def all_user():
    all_users = db_handler.get_all_users()
    friendship ={}
    for user in all_users:
        if user['username'] != current_user.username:
            this_user = db_handler.get_user_by_name(user['username'])
            if current_user.username in this_user[0]['followers']:
                friendship[user['username']] = True
                print(user['username'] + "true")
            else:
                friendship[user['username']] = False
                print(user['username'] + "false")
    return render_template("all_user.html", user=all_users, friendship=friendship)


'''
update the actual profile picture
'''
@app.route('/profile_pic_upload', methods=['GET', 'POST'])
def profile_pic_upload():
    return render_template("upload_profile_pic.html")