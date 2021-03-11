from awshandler import *
from awsconfig import *
from datetime import datetime, timedelta
from operator import itemgetter


aws_workers_dict = {}
aws_worker_dict_mutex = Lock()


'''Create one EC2 instance, return instance id
'''
def create_instance():
    # TODO
    return


'''Terminate one EC2 instance given instance id
'''
def terminate_instance(inst_id):
    ec2 = get_ec2()
    response = ec2.terminate_instances(InstanceIds=[inst_id])
    print("terminate inst {} response {}".format(inst_id, response))


'''Register one EC2 instancce to ELB given instance id
'''
def register_instance_to_elb(inst_id):
    elb = get_elb()
    response = elb.register_targets(
        TargetGroupArn=AWS_TARGET_GROUP_CONFIG['targetgroupARN'],
        Targets=[{'Id': inst_id, 'Port': 5000}]
    )
    print("register inst {} to elb response: {}".format(inst_id, response))


'''Deregisiter one EC2 instance given instance id
'''
def deregister_instance_to_elb(inst_id):
    elb = get_elb()
    response = elb.deregister_targets(
        TargetGroupArn=AWS_TARGET_GROUP_CONFIG['targetgroupARN'],
        Targets=[{'Id': inst_id, 'Port': 5000}]
    )
    print("deregister inst {} to elb response: {}".format(inst_id, response))


'''Scale up/down number of EC2 instances:
AWS_EC2_SCALING_UP: create instance -> add to worker dict (does not register to elb)
AWS_EC2_SCALING_DOWN: terminate instance -> change to stopping state -> deregister to elb
'''
def scaling_instance(scaling_behaviour, scaling_num):
    if scaling_behaviour == AWS_EC2_SCALING_UP:
        if len(aws_workers_dict) + scaling_num > AWS_EC2_NUM_MAX:
            return AWS_ERROR_EC2_NUM_EXCEED_MAX
        for num in range(scaling_num):
            inst_id = create_instance()
            with aws_worker_dict_mutex:
                aws_workers_dict[inst_id] = AWS_EC2_STATUS_PENDING
            print("Create instance with id : {}".format(inst_id))
        return AWS_OK
    
    if scaling_behaviour == AWS_EC2_SCALING_DOWN:
        if len(aws_workers_dict) - scaling_num < AWS_EC2_NUM_MIN:
            return AWS_ERROR_EC2_NUM_BELOW_MIN
        detach_cnt = 0
        with aws_worker_dict_mutex:
            for inst_id in aws_workers_dict:
                if detach_cnt > scaling_num:
                    break
                deregister_instance_to_elb(inst_id)
                terminate_instance(inst_id)
                aws_workers_dict[inst_id] = AWS_EC2_STATUS_STOPPING
                detach_cnt += 1
        return AWS_OK


'''Update aws_worker_dict status
PENDING -> RUNNING, and register to elb
STOPPING -> TERMINATED
'''
def update_aws_worker_dict():
    ec2_resource = get_ec2_resource()
    ec2_instances = ec2_resource.instancces.all()
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
            aws_workers_dict[inst_id] = AWS_EC2_STATUS_DOWN
    return AWS_OK


'''Get DNS from ELB for user app access
'''
def get_elb_dns():
    return AWS_ELB_CONFIG['lbDNS']


'''Get the number of workers for the past 30 minutes
'''
def get_ec2_workers_chart():
    cloudwatch = get_cloudwatch()
    current_time
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


'''Get CPU Utilization given by instance id
'''
def get_ec2_cpu_utilization(inst_id):
    cloudwatch = get_cloudwatch()
    current_time = datetime.utcnow()
    response = cloudwatch.get_metric_statistics(
        Period=60,
        StartTime=current_time-timedelta(seconds=1800),
        EndTime=current_time,
        MetricName=AWS_CLOUDWATCH_CONFIG['CPUUtilization'],
        Namespace=AWS_CLOUDWATCH_CONFIG['ec2_namespace'],
        Statistics=[AWS_CLOUDWATCH_CONFIG['statistics_avg']],
        Dimensions=[{'Name': 'InstanceId', 'Value': inst_id}]
    )
    return aws_datapoint_parser(response['Datapoints'], AWS_CLOUDWATCH_CONFIG['statistics_avg'])


'''Parse aws response datapoint
RETURN [[time, data]]
'''
def aws_datapoint_parser(data, statistics):
    ret_list = []
    for data_point in data:
        time = data_point['Timestamp'].hour + data_point['Timestamp'].minute/60
        ret_list.append([time, data_point[statistics]])
    ret_list = sorted(ret_list, key=itemgetter(0))
    return ret_list

