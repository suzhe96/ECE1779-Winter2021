import mysql.connector
from flask import g
from app import a1_webapp
from app.dbconfig import *


def connect_to_database_debug():
    return mysql.connector.connect(user=DATABASE_LOCAL_CONFIG['user'],
                                   password=DATABASE_LOCAL_CONFIG['password'],
                                   host=DATABASE_LOCAL_CONFIG['host'],
                                   database=DATABASE_LOCAL_CONFIG['db'])


def connect_to_database():
    return mysql.connector.connect(user=DATABASE_AWS_RDS_CONFIG['user'],
                                   password=DATABASE_AWS_RDS_CONFIG['password'],
                                   host=DATABASE_AWS_RDS_CONFIG['host'],
                                   database=DATABASE_AWS_RDS_CONFIG['db'])


def get_db(Debug=False):
    db = getattr(g, '_database', None)
    if db is None:
        if Debug:
            db = g._database = connect_to_database_debug()
        else:
            db = g._database = connect_to_database()
    return db


@a1_webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()