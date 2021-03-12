import time

from threading import Thread
from app import awsworker

# deefault policy
auto_scaler_policy = {'cpu_grow_threshold' : 80,
          'cpu_shrink_threshold' : 5,
          'cpu_grow_ratio' : 2,
          'cpu_shrink_ratio' : 0.5}
# policy mutex
auto_scaler_policy_mutex = Lock()


def auto_scaler_policy_set(cpu_grow_threshold,
                           cpu_shrink_threshold,
                           cpu_grow_ratio,
                           cpu_shrink_ratio):
    with auto_scaler_policy_mutex:
        auto_scaler_policy['cpu_grow_threshold'] = cpu_grow_threshold
        auto_scaler_policy['cpu_shrink_threshold'] = cpu_shrink_threshold
        auto_scaler_policy['cpu_grow_ratio'] =cpu_grow_ratio
        auto_scaler_policy['cpu_shrink_ratio'] = cpu_shrink_ratio


def auto_scaler_policy_get():
    with auto_scaler_policy_mutex:
        return auto_scaler_policy


def auto_scaler_main():
    # update aws_worker_dict
    awsworker.update_aws_worker_dict()
    # get aws_worker_dict
    worker_dict = awsworker.get_aws_worker_dict()
    # get cpu_utilization_avg
    cpu_util_avg = awsworker.get_ec2_cpu_utilization_avg(worker_dict)
    if cpu_util_avg == 0:
        # A running instance with hosting web application could not be 0 cpu in avg
        print("cpu_util_avg is 0!")
        return
    # get auto_scaler_policy
    policy = auto_scaler_policy_get()

    ret = AWS_OK
    # case: scale up
    if cpu_util_avg >= policy['cpu_grow_threshold']:
        scale_up_number = int(len(worker_dict) * policy['cpu_grow_ratio'])
        scale_up_number = max(0, scale_up_number)
        ret = awsworker.scaling_instance(AWS_EC2_SCALING_UP, scale_up_number)

    # case: scale down
    if cpu_util_avg <= policy['cpu_shrink_threshold']:
        scale_down_number = int(len(worker_dict) * policy['cpu_shrink_ratio'])
        scale_down_number = max(0, scale_down_number)
        ret = awsworker.scaling_instance(AWS_EC2_SCALING_DOWN, scale_down_number)

    if ret != AWS_OK:
        print("auto scaler error: {}".format(AWS_ERROR_MSG[ret]))

def auto_scaler_task_cb():
    while True:
        auto_scaler_main()
        time.sleep(60)