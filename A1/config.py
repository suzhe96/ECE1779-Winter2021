import os
import pymysql
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    APP_NAME = "ECE1779 A1"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    EMAIL_SUBJECT_PREFIX = '{app_name} Admin <{email}>'.format(
        app_name=APP_NAME, email='kevingarnett03@gmail.com')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'ece1779a1winter2021@gmail.com'
    MAIL_PASSWORD = '88admin88'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    ADMIN_USER = 'admin'

 
'''
Database initialization
'''
db_conn = None
cur_config = None
# will need to install mysql and set up user info
# run the schema.sql to set up the database with schema tables and initial data


DATABASE_LOCAL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "admin",
    "password": "ece1779pass",
    "db": "a1db"
}
DATABASE_AWS_RDS_CONFIG = {
    "host": "mydb.csj4dy0yam3g.us-east-1.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "ece1779pass",
    "db": "mydb"
}

# initialize the database connection with app
def init_db(env):
    global db_conn
    global cur_config

    #db_conn = pymysql.connect(**DATABASE_LOCAL_CONFIG)
    #cur_config = DATABASE_LOCAL_CONFIG

    # AWS RDS set up
    db_conn = pymysql.connect(**DATABASE_AWS_RDS_CONFIG)
    cur_config = DATABASE_AWS_RDS_CONFIG

def get_conn():
    global db_conn
    global cur_config
    if not db_conn or not db_conn.open:
        db_conn = pymysql.connect(**cur_config)
    return db_conn

# close database connection
def close_db():
    db_conn.close()
