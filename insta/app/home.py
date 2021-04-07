from flask import render_template, redirect, url_for, jsonify, request
from app import app
from flask_login import current_user
import json
import os
user = {}


@app.route('/', methods=['GET', 'POST'])
def main():
    if current_user.is_anonymous:
        return render_template("home.html")
    else:
        filename = os.path.join(app.static_folder, 'current_user.json')
        with open(filename) as json_file:
            user = json.load(json_file)
            friend = False
            for follower in user['followers']:
                if current_user.username == follower['username']:
                    friend = True
                    break
            print(friend)
            return render_template("profile.html", user=user, friend=friend, is_me=True)


@app.route('/index', methods=['GET', 'POST'])
def index():
    filename = os.path.join(app.static_folder, 'current_user.json')
    with open(filename) as json_file:
        user = json.load(json_file)
        return render_template("index.html", title="Feed", user=user, func=update_likes)



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


@app.route('/follow', methods=['GET', 'POST'])
def follow():
    print("follow")
    filename = os.path.join(app.static_folder, 'current_user.json')
    with open(filename) as json_file:
        user = json.load(json_file)
        #need to add the friend to the db
        return render_template("profile.html", user=user, friend=True, is_me=False)


@app.route('/unfollow', methods=['GET', 'POST'])
def unfollow():
    print("unfollow")
    filename = os.path.join(app.static_folder, 'current_user.json')
    with open(filename) as json_file:
        user = json.load(json_file)
        #need to unfriend in the db
        return render_template("profile.html", user=user, friend=False, is_me=False)


#change the profile picture
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    print("edit_profile")
    return redirect(url_for('index'))


@app.route('/change_profile_bio', methods=['GET', 'POST'])
def change_profile_bio():
    # need to change the bio for current user in the db
    return redirect(url_for('index'))


@app.route('/followers', methods=['GET', 'POST'])
def followers():
    # need to change the bio for current user in the db
    return redirect(url_for('index'))


@app.route('/followings', methods=['GET', 'POST'])
def followings():
    # need to change the bio for current user in the db
    return redirect(url_for('index'))


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    # need to change the bio for current user in the db
    return redirect(url_for('index'))