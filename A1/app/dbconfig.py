
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
    "aws_access_key": "AKIAUA6L6EDR3WYDNCPU",
    "aws_secret_access_key": "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",
    "aws_bucket_name": "a1-db",
    "aws_s3_bucket_url": "https://a1-db.s3.amazonaws.com/{}",
}
