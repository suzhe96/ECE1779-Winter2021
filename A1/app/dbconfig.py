
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
    "aws_iam_role": "ECE1779-ADMIN",
    "aws_bucket_name": "a1db",
    "aws_s3_bucket_url": "https://a1db.s3.amazonaws.com/{}",
}

# AWS personal credentials
AWS_CREDENTIALS_PERSONAL = {
    "aws_access_key": "*****",
    "aws_secret_access_key": "*****", 
}

DEPLOY_BUILT = False
AWS_CREDENTIALS_REQUEST = "http://169.254.169.254/latest/meta-data/iam/security-credentials/{}"