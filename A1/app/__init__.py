from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from threading import Thread


app = Flask(__name__)

from app import home, user, models, detector
from app import awsconfig, awshandler, awsworker

app.config.from_object(Config)
sqlalchemy_url = 'mysql+pymysql://{}:{}@{}/{}'
if awsconfig.AWS_RDS_DEPLOY:
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_url.format(
        awsconfig.AWS_RDS_CONFIG['user'],
        awsconfig.AWS_RDS_CONFIG['password'],
        awsconfig.AWS_RDS_CONFIG['host'],
        awsconfig.AWS_RDS_CONFIG['db']
    ) 
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_url.format(
        awsconfig.DATABASE_LOCAL_CONFIG['user'],
        awsconfig.DATABASE_LOCAL_CONFIG['password'],
        awsconfig.DATABASE_LOCAL_CONFIG['host'],
        awsconfig.DATABASE_LOCAL_CONFIG['db']
    ) 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

http_request_backgroud_task = Thread(target=awsworker.publish_http_request_cb)
http_request_backgroud_task.daemon = True
http_request_backgroud_task.start()
