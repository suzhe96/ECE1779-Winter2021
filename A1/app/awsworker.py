import time
from app.awshandler import *
from app.awsconfig import *
from datetime import datetime, timedelta
from operator import itemgetter
from threading import Lock

http_request_count = 0
http_request_count_mutex = Lock()


def add_http_request_count():
    global http_request_count 
    with http_request_count_mutex:
        http_request_count += 1


def get_and_reset_http_request_count():
    global http_request_count
    with http_request_count_mutex:
        ret_val = http_request_count
        http_request_count = 0
    return ret_val


def publish_http_request_count(inst_id):
    cloudwatch = get_cloudwatch()
    current_time = datetime.utcnow()
    requests_count = get_and_reset_http_request_count()
    print("Request count {} from worker {}".format(requests_count, inst_id))
    cloudwatch.put_metric_data(Namespace=AWS_CLOUDWATCH_CONFIG['http_namespace'],
                               MetricData=[{'MetricName' : AWS_CLOUDWATCH_CONFIG['http_metrics'],
                                            'Timestamp' : current_time,
                                            'Value' : requests_count,
                                            'Unit' : 'Count',
                                            'Dimensions' : [{
                                                'Name' : 'InstanceId',
                                                'Value' : inst_id
                                            }]
                                           }])
    print("worker {} update http request metric".format(inst_id))


def publish_http_request_cb():
    inst_id = get_instance_id()
    while True:
        publish_http_request_count()
        time.sleep(60)


