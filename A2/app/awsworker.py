from app.awshandler import *
from app.awsconfig import *
from datetime import datetime, timedelta
from operator import itemgetter
from threading import Lock
import mysql.connector

aws_workers_dict = {}
aws_worker_dict_mutex = Lock()


'''Create one EC2 instance, return instance id
RETURN instance_id
'''
def create_instance():
    ec2_resource = get_ec2_resource()
    instance_list = ec2_resource.create_instances(MaxCount=1,
                                                  MinCount=1,
                                                  LaunchTemplate={'LaunchTemplateId': AWS_LAUNCH_TEMPLATE_CONFIG['id'],
                                                                  'Version': AWS_LAUNCH_TEMPLATE_CONFIG['version']})
    print("Instance created: {}".format(instance_list[0].id))
    return instance_list[0].id


'''Terminate one EC2 instance given instance id
'''
def terminate_instance(inst_id):
    ec2 = get_ec2()
    response = ec2.terminate_instances(InstanceIds=[inst_id])
    print("Instance terminated: {}".format(inst_id))


'''Stop one EC2 instance given instance id
'''
def stop_instance(inst_id):
    ec2 = get_ec2()
    response = ec2.stop_instances(InstanceIds=[inst_id])
    print("Instance stopped: {}".format(inst_id))


'''Register one EC2 instancce to ELB given instance id
'''
def register_instance_to_elb(inst_id):
    elb = get_elb()
    response = elb.register_targets(
        TargetGroupArn=AWS_TARGET_GROUP_CONFIG['targetgroupARN'],
        Targets=[{'Id': inst_id, 'Port': 5000}]
    )
    print("Instance registed to elb: {}".format(inst_id))


'''Deregisiter one EC2 instance given instance id
'''
def deregister_instance_to_elb(inst_id):
    elb = get_elb()
    response = elb.deregister_targets(
        TargetGroupArn=AWS_TARGET_GROUP_CONFIG['targetgroupARN'],
        Targets=[{'Id': inst_id, 'Port': 5000}]
    )
    print("Instance deregisted to elb: {}".format(inst_id))


'''Scale up/down number of EC2 instances:
AWS_EC2_SCALING_UP: create instance -> add to worker dict (does not register to elb)
AWS_EC2_SCALING_DOWN: terminate instance -> change to stopping state -> deregister to elb
'''
def scaling_instance(scaling_behaviour, scaling_num):
    with aws_worker_dict_mutex:
        if scaling_behaviour == AWS_EC2_SCALING_UP:
            if len(aws_workers_dict) + scaling_num > AWS_EC2_NUM_MAX:
                return AWS_ERROR_EC2_NUM_EXCEED_MAX
            for inst_id in aws_workers_dict:
                if aws_workers_dict[inst_id] == AWS_EC2_STATUS_PENDING:
                    scaling_num -= 1
            scaling_num = max(0, scaling_num)
            print("Actual scale up number: {}".format(scaling_num))
            if (scaling_num == 0):
                return AWS_ERROR_EC2_NUM_SCALE_ZERO
            for num in range(scaling_num):
                inst_id = create_instance()
                aws_workers_dict[inst_id] = AWS_EC2_STATUS_PENDING

        if scaling_behaviour == AWS_EC2_SCALING_DOWN:
            if len(aws_workers_dict) - scaling_num < AWS_EC2_NUM_MIN:
                return AWS_ERROR_EC2_NUM_BELOW_MIN
            stopping_list = []
            pending_list = []
            running_list = []
            for inst_id in aws_workers_dict:
                if aws_workers_dict[inst_id] == AWS_EC2_STATUS_STOPPING:
                    stopping_list.append(inst_id)
                elif aws_workers_dict[inst_id] == AWS_EC2_STATUS_PENDING:
                    pending_list.append(inst_id)
                elif aws_workers_dict[inst_id] == AWS_EC2_STATUS_RUNNING:
                    running_list.append(inst_id)
            scaling_num = max(0, scaling_num - len(stopping_list))
            print("Actual scale down number: {}".format(scaling_num))
            if scaling_num == 0:
                return AWS_ERROR_EC2_NUM_SCALE_ZERO

            '''Terminate instance:
            Remove any pending instance first since it has not contributed to the work
            Remove the running instance reversely since the last one has the 
            largest possibility to be unhealthy
            '''
            for inst_id in pending_list:
                if scaling_num == 0:
                    break
                deregister_instance_to_elb(inst_id)
                terminate_instance(inst_id)
                aws_workers_dict[inst_id] = AWS_EC2_STATUS_STOPPING
                scaling_num -= 1
            for index in range(len(running_list)-1, -1, -1):
                if scaling_num == 0:
                    break
                deregister_instance_to_elb(running_list[index])
                terminate_instance(running_list[index])
                aws_workers_dict[running_list[index]] = AWS_EC2_STATUS_STOPPING
                scaling_num -= 1
    return AWS_OK


'''Update aws_worker_dict status
PENDING -> RUNNING, and register to elb
STOPPING -> TERMINATED
'''
def update_aws_worker_dict():
    ec2_resource = get_ec2_resource()
    ec2_instances = ec2_resource.instances.all()
    pending_to_running, stopping_to_down = [], []
    with aws_worker_dict_mutex:
        for inst in ec2_instances:
            if inst.id not in aws_workers_dict:
                continue
            if aws_workers_dict[inst.id] == AWS_EC2_STATUS_PENDING and inst.state['Name'] == AWS_EC2_STATUS_RUNNING:
                pending_to_running.append(inst.id)
            if aws_workers_dict[inst.id] == AWS_EC2_STATUS_STOPPING and inst.state['Name'] == AWS_EC2_STATUS_DOWN:
                stopping_to_down.append(inst.id)

        for inst_id in pending_to_running:
            register_instance_to_elb(inst_id)
            aws_workers_dict[inst_id] = AWS_EC2_STATUS_RUNNING
        for inst_id in stopping_to_down:
            del aws_workers_dict[inst_id]
    return AWS_OK


'''Get DNS from ELB for user app access
'''
def get_elb_dns():
    return AWS_ELB_CONFIG['lbDNS']


'''Get the number of workers for the past 30 minutes
'''
def get_ec2_workers_chart():
    cloudwatch = get_cloudwatch()
    current_time = datetime.utcnow()
    response = cloudwatch.get_metric_statistics(
        Period=60,
        StartTime=current_time-timedelta(seconds=1800),
        EndTime=current_time,
        MetricName=AWS_CLOUDWATCH_CONFIG['healthy_metrics'],
        Namespace=AWS_CLOUDWATCH_CONFIG['elb_namespace'],
        Statistics=[AWS_CLOUDWATCH_CONFIG['statistics_avg']],
        Dimensions=[{'Name': 'TargetGroup', 'Value': AWS_TARGET_GROUP_CONFIG['targetgroup']},
                    {'Name': 'LoadBalancer', 'Value': AWS_ELB_CONFIG['lb']}]
    )
    return aws_datapoint_parser(response['Datapoints'], AWS_CLOUDWATCH_CONFIG['statistics_avg'])


'''Get CPU utilization given by instance id
'''
def get_ec2_cpu_utilization(inst_id):
    cloudwatch = get_cloudwatch()
    current_time = datetime.utcnow()
    response = cloudwatch.get_metric_statistics(
        Period=60,
        StartTime=current_time-timedelta(seconds=1800),
        EndTime=current_time,
        MetricName=AWS_CLOUDWATCH_CONFIG['CPU_metrics'],
        Namespace=AWS_CLOUDWATCH_CONFIG['ec2_namespace'],
        Statistics=[AWS_CLOUDWATCH_CONFIG['statistics_avg']],
        Dimensions=[{'Name': 'InstanceId', 'Value': inst_id}]
    )
    return aws_datapoint_parser(response['Datapoints'], AWS_CLOUDWATCH_CONFIG['statistics_avg'])


'''Get CPU Utilization for all workers
'''
def get_all_ec2_cpu_utilizaton(worker_dict):
    all_running_ec2_stat ={}
    index = 0
    for inst_id in worker_dict:
    #    if worker_dict[inst_id] != AWS_EC2_STATUS_RUNNING:
    #        continue
        ec2_stat = get_ec2_cpu_utilization(inst_id);
        all_running_ec2_stat[index] = ec2_stat
        index = index + 1
    return all_running_ec2_stat


'''Get CPU utilization average value given up-to-dated worker_dict (ONLY COUNT ON RUNNING INSTANCES)
'''
def get_ec2_cpu_utilization_avg(healthy_dict):
    cpu_avg_list = []
    for inst_id in healthy_dict:
        if healthy_dict[inst_id] != AWS_ELB_TARGET_STATUS_HEALTHY:
            continue
        response = get_ec2_cpu_utilization(inst_id)
        datapoints = response[1][-2:]
        if len(datapoints) != 0:
            cpu_avg_list.append(sum(datapoints) / len(datapoints))
    if len(cpu_avg_list) != 0:
        return sum(cpu_avg_list) / len(cpu_avg_list)
    return AWS_ERROR_CPU_AVG_VALUE_ZERO


'''GET HTTP Requests for all running worker instances
'''
def get_all_workers_http_request(worker_dict):
    all_running_ec2_stat ={}
    index = 0
    for inst_id in worker_dict:
    #    if worker_dict[inst_id] != AWS_EC2_STATUS_RUNNING:
    #        continue
        ec2_stat = get_http_request(inst_id);
        all_running_ec2_stat[index] = ec2_stat
        index = index + 1
    return all_running_ec2_stat


'''Get HTTP Requests given by instance id
'''
def get_http_request(inst_id):
    cloudwatch = get_cloudwatch()
    current_time = datetime.utcnow()
    response = cloudwatch.get_metric_statistics(
        Period=60,
        StartTime=current_time-timedelta(seconds=1800),
        EndTime=current_time,
        MetricName=AWS_CLOUDWATCH_CONFIG['http_metrics'],
        Namespace=AWS_CLOUDWATCH_CONFIG['http_namespace'],
        Statistics=[AWS_CLOUDWATCH_CONFIG['statistics_sum']],
        Dimensions=[{'Name': 'InstanceId', 'Value': inst_id}]
    )
    return aws_datapoint_parser(response['Datapoints'], AWS_CLOUDWATCH_CONFIG['statistics_sum']) 


'''Parse aws response datapoint
RETURN [[time, data]]
'''
def aws_datapoint_parser(data, statistics):
    ret_list = []
    stat =[]
    time_stamps =[]
    for data_point in data:
        time = data_point['Timestamp'].hour + data_point['Timestamp'].minute/60
        time_stamps.append(round(time,2))
        stat.append(data_point[statistics])
    indexes = list(range(len(time_stamps)))
    indexes.sort(key=time_stamps.__getitem__)
    time_stamps = list(map(time_stamps.__getitem__, indexes))
    stat = list(map(stat.__getitem__, indexes))
    ret_list=[time_stamps, stat]
                
    return ret_list


'''Initalize the first worker
'''
def initialize_first_worker():
    print("========== START INIT FIRST WORKER ==========")
    scaling_instance(AWS_EC2_SCALING_UP, 1)
    print("==========  END INIT FIRST WORKER  ==========")


'''Get worker dict
'''
def get_aws_worker_dict():
    return aws_workers_dict 


'''Terminate all worke instances and stop manager instance
'''
def stop_all():
    ec2_resource = get_ec2_resource()
    ec2_instances = ec2_resource.instances.all()
    for inst in ec2_instances:
        if inst.state['Name'] != AWS_EC2_STATUS_DOWN: 
            if inst.id == AWS_GENERAL_CONFIG['manager_inst_id']:
                stop_instance(inst.id)
            else:
                terminate_instance(inst.id)
    return AWS_OK


'''Init RDB with schema.sql
'''
def init_rdb():
    cmd_list = []
    with open("schema.sql") as fd:
        cmd_list = [cmd.replace("\n", "") for cmd in fd.read().split(";")]
    cnx = get_db()
    cursor = cnx.cursor()
    for cmd in cmd_list:
        if not cmd: continue
        cursor.execute(cmd)
        cnx.commit()


'''Get healthy instances from ELB
'''
def get_healthy_instances():
    elb = get_elb()
    response = elb.describe_target_health(
        TargetGroupArn=AWS_TARGET_GROUP_CONFIG['targetgroupARN'],
    )
    ret_dict = {}
    if response is None or len(response) == 0 or 'TargetHealthDescriptions' not in response:
        return ret_dict

    for attr in response['TargetHealthDescriptions']:
        ret_dict[attr['Target']['Id']] = attr['TargetHealth']['State']
    return ret_dict