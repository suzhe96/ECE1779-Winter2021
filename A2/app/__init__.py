from flask import Flask
from config import Config
from threading import Thread


a2 = Flask(__name__)
a2.config.from_object(Config)

from app import home, form
from app import awsworker
from app import autoscaler

awsworker.initialize_first_worker()

auto_scaler_background_task = Thread(target=autoscaler.auto_scaler_task_cb)
auto_scaler_background_task.daemon = True
auto_scaler_background_task.start()