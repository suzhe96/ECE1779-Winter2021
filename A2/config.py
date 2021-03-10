import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # ...
    APP_NAME = "ECE1779 A2"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    EMAIL_SUBJECT_PREFIX = '{app_name} Admin <{email}>'.format(
        app_name=APP_NAME, email='ece1779a1winter2021.com')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'ece1779a1winter2021@gmail.com'
    MAIL_PASSWORD = '88admin88'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    ADMIN_USER = 'admin'

