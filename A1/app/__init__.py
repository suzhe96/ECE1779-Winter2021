from flask import Flask
from config import Config
a1_webapp = Flask(__name__)
a1_webapp.config.from_object(Config)

from app import home
from app import user

