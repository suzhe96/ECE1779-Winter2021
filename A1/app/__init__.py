from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from threading import Thread


a1_webapp = Flask(__name__)
a1_webapp.config.from_object(Config)
a1_webapp.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ece1779pass@localhost/ECE1779_A1_DB'
db = SQLAlchemy(a1_webapp)
bcrypt = Bcrypt(a1_webapp)
login_manager = LoginManager(a1_webapp)
login_manager.login_view = 'login'

from app import home, user, models, detector
from app import awsconfig, awshandler, awsworker

http_request_backgroud_task = Thread(target=awsworker.publish_http_request_cb)
http_request_backgroud_task.daemon = True
http_request_backgroud_task.start()
