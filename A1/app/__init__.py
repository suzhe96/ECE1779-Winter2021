from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from threading import Thread


app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ece1779pass@localhost/ECE1779_A1_DB'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import home, user, models, detector
from app import awsconfig, awshandler, awsworker

http_request_backgroud_task = Thread(target=awsworker.publish_http_request_cb)
http_request_backgroud_task.daemon = True
http_request_backgroud_task.start()
