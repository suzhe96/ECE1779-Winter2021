
# Deploy by using local config require MySql server on local system
DATABASE_LOCAL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "ece1779pass",
    "db": "ECE1779_A1_DB"
}

# S3 bucket need to be pre-created as public access
AWS_S3_CONFIG = {
    "aws_bucket_name": "a1db",
    "aws_s3_bucket_url": "https://a1db.s3.amazonaws.com/{}",
}

# AWS personal credentials
AWS_CREDENTIALS_PERSONAL = {
    "aws_access_key": "*****",
    "aws_secret_access_key": "*****", 
}

AWS_CREDENTIALS_CONFIG = {
    'request'  : 'http://169.254.169.254/latest/meta-data/iam/security-credentials/{}',
    'request_inst_id' : 'http://169.254.169.254/latest/meta-data/instance-id/',
    'iam_role' : 'ECE1779-ADMIN'
}

AWS_GENERAL_CONFIG = {
    'region' : 'us-east-1',
    's3_service' : 's3',
    'cloudwatch_service' : 'cloudwatch'
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
}