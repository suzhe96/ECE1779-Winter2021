from flask import render_template
from app import a1_webapp
from app.awshandler import get_db
from flask_login import current_user
from app import awsworker


@a1_webapp.route('/')
@a1_webapp.route('/home')
def main():
    # awsworker.add_http_request_count()
    # print("/home add")
    if current_user.is_anonymous:
        return render_template("home.html", title="Home")

    __username = current_user.username
    print("__username:{}".format(__username))
    print("{}".format(type(__username)))
    cnx = get_db()
    cursor = cnx.cursor()
    try:
        query = '''SELECT images.image_url, images.category FROM users, images WHERE users.id = images.user_id AND users.username = %s;'''
        cursor.execute(query, (__username,))
        row = cursor.fetchall()
        if not row:
            print("Get image empty row")
            # raise Exception('Get image empty row')
    except:
        raise Exception('Get query from RDB exception')

    category1, category2, category3, category4 = [], [], [], []
    for i in row:
        if (i[1] == 1): category1.append(i[0])
        if (i[1] == 2): category2.append(i[0])
        if (i[1] == 3): category3.append(i[0])
        if (i[1] == 4): category4.append(i[0])
    category_dict = {"1":category1, "2":category2, "3":category3, "4":category4}
    return render_template("home.html", title="Home", param=category_dict)