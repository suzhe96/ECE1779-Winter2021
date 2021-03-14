AWS_CREDENTIALS_CONFIG = {
    'request'  : 'http://169.254.169.254/latest/meta-data/iam/security-credentials/{}',
    'iam_role' : 'ECE1779-ADMIN'
}

AWS_ELB_CONFIG = {
    'lb' : 'app/ece1779-lb-group-zhe/70e467fa27db17ed',
    'lbARN' : 'arn:aws:elasticloadbalancing:us-east-1:905405143286:loadbalancer/app/ece1779-lb-group-zhe/70e467fa27db17ed',
    'lbDNS' : 'ece1779-lb-group-zhe-1258727599.us-east-1.elb.amazonaws.com'
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
    'version' : '14'
}

AWS_EC2_STATUS_PENDING = 'pending'
AWS_EC2_STATUS_RUNNING = 'running'
AWS_EC2_STATUS_STOPPING = 'stopping'
AWS_EC2_STATUS_DOWN = 'terminated'

AWS_EC2_SCALING_UP = 'up'
AWS_EC2_SCALING_DOWN = 'down'

AWS_EC2_NUM_MAX = 8
AWS_EC2_NUM_MIN = 1

AWS_OK = 0
AWS_ERROR_EC2_NUM_EXCEED_MAX = 1501
AWS_ERROR_EC2_NUM_BELOW_MIN = 1502
AWS_ERROR_CPU_AVG_VALUE_ZERO = 1503

AWS_ERROR_MSG = {
   AWS_ERROR_EC2_NUM_EXCEED_MAX : 'EC2 instance number maximum reached',
   AWS_ERROR_EC2_NUM_BELOW_MIN : 'EC2 instance number minimum reached',
   AWS_ERROR_CPU_AVG_VALUE_ZERO : 'Get zero in cpu utilization average'
}

# Could be included into launchTemplate
AWS_EC2_USERDATA_SCRIPT = 'Content-Type: multipart/mixed; boundary="//"\n' \
                          'MIME-Version: 1.0\n' \
                          '--//\n' \
                          'Content-Type: text/cloud-config; charset="us-ascii"\n' \
                          'MIME-Version: 1.0\n' \
                          'Content-Transfer-Encoding: 7bit\n' \
                          'Content-Disposition: attachment; filename="cloud-config.txt"\n' \
                          '#cloud-config\n' \
                          'cloud_final_modules:\n' \
                          '- [scripts-user, always]\n' \
                          '--//\n' \
                          'Content-Type: text/x-shellscript; charset="us-ascii"\n' \
                          'MIME-Version: 1.0\n' \
                          'Content-Transfer-Encoding: 7bit\n' \
                          'Content-Disposition: attachment; filename="userdata.txt"\n' \
                          '#!/bin/bash\n' \
                          'screen\n' \
                          '/home/ubuntu/Desktop/ECE1779-Winter2021/A1/start.sh\n' \
                          '--//'
