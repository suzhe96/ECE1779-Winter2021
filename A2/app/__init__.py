from flask import Flask
from config import Config


a2 = Flask(__name__)
a2.config.from_object(Config)

from app import home
