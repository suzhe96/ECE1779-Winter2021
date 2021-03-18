import time
from threading import Thread, Lock
from app import awsworker
from app.awsconfig import *
from app.awshandler import *

# deefault policy
auto_scaler_policy = {'cpu_grow_threshold' : 80,
          'cpu_shrink_threshold' : 5,
          'cpu_grow_ratio' : 2,
          'cpu_shrink_ratio' : 0.5}
# policy mutex
auto_scaler_policy_mutex = Lock()
AUTO_SCALER_POLICY_ID = 1


def auto_scaler_policy_set(cpu_grow_threshold,
                           cpu_shrink_threshold,
                           cpu_grow_ratio,
                           cpu_shrink_ratio):
    # with auto_scaler_policy_mutex:
    #     auto_scaler_policy['cpu_grow_threshold'] = cpu_grow_threshold
    #     auto_scaler_policy['cpu_shrink_threshold'] = cpu_shrink_threshold
    #     auto_scaler_policy['cpu_grow_ratio'] =cpu_grow_ratio
    #     auto_scaler_policy['cpu_shrink_ratio'] = cpu_shrink_ratio
    # store policy to db as required by handout
    with auto_scaler_policy_mutex:
        cnx = connect_to_database()
        cursor = cnx.cursor()
        query = '''UPDATE policy SET cpu_grow_threshold={}, cpu_shrink_threshold={}, cpu_grow_ratio={}, cpu_shrink_ratio={} WHERE id={}'''.format(
            cpu_grow_threshold,
            cpu_shrink_threshold,
            cpu_grow_ratio,
            cpu_shrink_ratio,
            AUTO_SCALER_POLICY_ID
        )
        cursor.execute(query)
        cnx.commit()


def auto_scaler_policy_get():
    with auto_scaler_policy_mutex:
        # return auto_scaler_policy
        cnx = connect_to_database()
        cursor = cnx.cursor()
        query = '''SELECT cpu_grow_threshold, cpu_shrink_threshold, cpu_grow_ratio, cpu_shrink_ratio FROM policy WHERE id={}'''.format(
            AUTO_SCALER_POLICY_ID
        )
        cursor.execute(query)
        policy_list = cursor.fetchone()
        cnx.commit()
        policy_dict = {'cpu_grow_threshold' : policy_list[0],
                       'cpu_shrink_threshold' : policy_list[1],
                       'cpu_grow_ratio' : policy_list[2],
                       'cpu_shrink_ratio' : policy_list[3]}
        return policy_dict


'''Work the best to converge:
We calculate the CPU avg on only healthy instances;
For scaling up:
If the instance started by the previous minute detection is running but not healthy,
a new instance should not be started since the current cpu avg does not include
the actual workloads from the previous minute started instance.
For scaling down:
This logic should not be applied to scaling down case since
the workload is below the threshold, we need to terminate a instance anyway
'''
def eligible_for_scaling_up(worker_dict, healthy_dict):
    running_count = 0
    healthy_count = 0
    for inst in worker_dict:
        if worker_dict[inst] == AWS_EC2_STATUS_RUNNING:
            running_count += 1
    for inst in healthy_dict:
        if healthy_dict[inst] == AWS_ELB_TARGET_STATUS_HEALTHY:
            healthy_count += 1
    return running_count == healthy_count



def auto_scaler_main():
    print("########## Autoscaler Thread ##########")
    # update aws_worker_dict
    awsworker.update_aws_worker_dict()
    # get aws_worker_dict
    worker_dict = awsworker.get_aws_worker_dict()
    print("worker_dict: {}".format(worker_dict))
    # get target healthy dict
    healthy_dict = awsworker.get_healthy_instances()
    print("healthy_dict: {}".format(healthy_dict))
    # get cpu_utilization_avg
    cpu_util_avg = awsworker.get_ec2_cpu_utilization_avg(healthy_dict)
    if cpu_util_avg == AWS_ERROR_CPU_AVG_VALUE_ZERO:
        # A running instance with hosting web application could not be 0 cpu in avg
        print("Info: {}".format(AWS_ERROR_MSG[AWS_ERROR_CPU_AVG_VALUE_ZERO]))
        print("It happends only at the first initialization of manager")
        print("######################################")
        return
    print("cpu utilization average: {}".format(cpu_util_avg))
    # get auto_scaler_policy
    policy = auto_scaler_policy_get()

    ret = AWS_OK
    # case: scale up
    if cpu_util_avg >= policy['cpu_grow_threshold']:
        if (eligible_for_scaling_up(worker_dict, healthy_dict) == False):
            print("Info: Wait for some running instances becoming healthy...")
            print("######################################")
            return 

        scale_up_number = int(len(worker_dict) * (policy['cpu_grow_ratio']-1))
        scale_up_number = max(0, scale_up_number)
        print("Behaviour: Scale up")
        print("Number: {}".format(scale_up_number))
        ret = awsworker.scaling_instance(AWS_EC2_SCALING_UP, scale_up_number)

    # case: scale down
    if cpu_util_avg <= policy['cpu_shrink_threshold']:
        scale_down_number = int(len(worker_dict) * (1-policy['cpu_shrink_ratio']))
        scale_down_number = max(0, scale_down_number)
        print("Behaviour: Scale down")
        print("Number: {}".format(scale_down_number))
        ret = awsworker.scaling_instance(AWS_EC2_SCALING_DOWN, scale_down_number)

    if ret != AWS_OK:
        print("Info: {}".format(AWS_ERROR_MSG[ret]))
    print("######################################")


def auto_scaler_task_cb():
    while True:
        auto_scaler_main()
        time.sleep(60)