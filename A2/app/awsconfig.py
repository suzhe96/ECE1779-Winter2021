AWS_CREDENTIALS_CONFIG = {
    'request'  : 'http://169.254.169.254/latest/meta-data/iam/security-credentials/{}',
    'iam_role' : 'ECE1779-ADMIN'
}

AWS_RDS_CONFIG = {
    "host": "ece1779-group-zhe-rds.cyxz2jq5daoc.us-east-1.rds.amazonaws.com",
    "port": 3306,
    "user": "root",
    "password": "ece1779pass",
    "db": "ECE1779_AUTO_SCALER_DB"
}

AWS_ELB_CONFIG = {
    'lb' : 'app/ece1779-lb-group-zhe/70e467fa27db17ed',
    'lbARN' : 'arn:aws:elasticloadbalancing:us-east-1:905405143286:loadbalancer/app/ece1779-lb-group-zhe/70e467fa27db17ed',
    'lbDNS' : 'ece1779-lb-group-zhe-1258727599.us-east-1.elb.amazonaws.com',
    'lbName' : 'ece1779-lb-group-zhe'
}

AWS_TARGET_GROUP_CONFIG = {
    'targetgroup' : 'targetgroup/ece1779-lb-target-group-zhe/674e2a3500167196',
    'targetgroupARN' : 'arn:aws:elasticloadbalancing:us-east-1:905405143286:targetgroup/ece1779-lb-target-group-zhe/674e2a3500167196'
}

AWS_GENERAL_CONFIG = {
    'region' : 'us-east-1',
    'manager_inst_id' : 'i-08e136084eb1c23c4',
    'elb_service' : 'elbv2',
    'ec2_service' : 'ec2',
    'cloudwatch_service' : 'cloudwatch',
    's3_service' : 's3'
}

AWS_CLOUDWATCH_CONFIG = {
    'elb_namespace' : 'AWS/ApplicationELB',
    'ec2_namespace' : 'AWS/EC2',
    'http_namespace' : 'HTTP/Requests',
    'CPU_metrics' : 'CPUUtilization',
    'healthy_metrics' : 'HealthyHostCount',
    'http_metrics' : 'HTTPRequestsMetrics',
    'statistics_avg' : 'Average',
    'statisitcs_max' : 'Maximum',
    'statistics_sum' : 'Sum',
}

AWS_LAUNCH_TEMPLATE_CONFIG = {
    'id' : 'lt-05d5dd91eddb6aee4',
    'version' : '16'
}

AWS_EC2_STATUS_PENDING = 'pending'
AWS_EC2_STATUS_RUNNING = 'running'
AWS_EC2_STATUS_STOPPING = 'stopping'
AWS_EC2_STATUS_DOWN = 'terminated'
AWS_ELB_TARGET_STATUS_HEALTHY = 'healthy'
AWS_ELB_TARGET_STATUS_UNHEALTHY = 'unhealthy'
AWS_ELB_TARGET_STATUS_INIT = 'initial'
AWS_ELB_TARGET_STATUS_UNUSED = 'unused'

AWS_EC2_SCALING_UP = 'up'
AWS_EC2_SCALING_DOWN = 'down'

AWS_EC2_NUM_MAX = 8
AWS_EC2_NUM_MIN = 1

AWS_OK = 0
AWS_ERROR_EC2_NUM_EXCEED_MAX = 1501
AWS_ERROR_EC2_NUM_BELOW_MIN = 1502
AWS_ERROR_CPU_AVG_VALUE_ZERO = 1503
AWS_ERROR_EC2_NUM_SCALE_ZERO = 1504

AWS_ERROR_MSG = {
   AWS_ERROR_EC2_NUM_EXCEED_MAX : 'EC2 instance number maximum reached',
   AWS_ERROR_EC2_NUM_BELOW_MIN : 'EC2 instance number minimum reached',
   AWS_ERROR_CPU_AVG_VALUE_ZERO : 'Get zero in cpu utilization average',
   AWS_ERROR_EC2_NUM_SCALE_ZERO : 'EC2 scaling with zero worker'
}

AWS_RDS_DEPLOY = True 

# Deploy by using local config require MySql server on local system
DATABASE_LOCAL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "ece1779pass",
    "db": "ECE1779_AUTO_SCALER_DB"
}

AWS_S3_WORKER_BUCKET = 'a1db'
