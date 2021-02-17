from flask import render_template
from app import a1_webapp
from app.dbhandler import get_db
from flask_login import current_user


@a1_webapp.route('/')
@a1_webapp.route('/home')
def main():
    if current_user.is_anonymous:
        return render_template("home.html", title="Home")

    __username = current_user.username
    print("__username:{}".format(__username))
    print("{}".format(type(__username)))
    cnx = get_db(Debug=True)
    cursor = cnx.cursor()
    try:
        query = '''SELECT images.image_key, images.category FROM users, images WHERE users.id = images.user_id AND users.username = %s;'''
        cursor.execute(query, (__username,))
        row = cursor.fetchall()
        if not row:
            print("Get image empty row")
            # raise Exception('Get image empty row')
    except:
        raise Exception('Get query from RDB exception')

    for i in row:
        print('row: {}'.format(i))

    return render_template("home.html", title="Home")