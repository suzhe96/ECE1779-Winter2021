from flask import Flask
from config import Config


a2 = Flask(__name__)
a2.config.from_object(Config)

from app import home
from app import awsworker



print("im here ready for resting {}".format(awsworker.get_elb_dns()))
print("====================================")
print("CPU: {}".format(awsworker.get_ec2_cpu_utilization('i-0f2ab4d996f0af8aa')))
print("===============================DONE1===")
print("====================================")
print("CPU: {}".format(awsworker.get_ec2_workers_chart()))
print("===============================DONE2===")