from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
# FIXME,delete flask_migrate after
from flask_migrate import Migrate
from flask_login import LoginManager


a1_webapp = Flask(__name__)
a1_webapp.config.from_object(Config)
db = SQLAlchemy(a1_webapp)
migrate = Migrate(a1_webapp, db)
login_manager = LoginManager(a1_webapp)
login_manager.login_view = 'login'

from app import home, user, models