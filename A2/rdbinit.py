import mysql.connector


AWS_RDS_CONFIG = {
    "host": "ece1779-group-zhe-rds.cyxz2jq5daoc.us-east-1.rds.amazonaws.com",
    "port": 3306,
    "user": "root",
    "password": "ece1779pass",
    "db": "ECE1779_A1_DB"
}

DATABASE_LOCAL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "ece1779pass",
    "db": "ECE1779_A1_DB"
}


AWS_RDS_DEPLOY = False


def init_rds_script():
    cmd_list = []
    with open("schema.sql") as fd:
        cmd_list = [cmd.replace("\n", "") for cmd in fd.read().split(";")]
    if AWS_RDS_DEPLOY:
        cnx = mysql.connector.connect(user=AWS_RDS_CONFIG['user'],
                                      password=AWS_RDS_CONFIG['password'],
                                      host=AWS_RDS_CONFIG['host'],
                                      database=AWS_RDS_CONFIG['db'])
    else:
        cnx = mysql.connector.connect(user=DATABASE_LOCAL_CONFIG['user'],
                                      password=DATABASE_LOCAL_CONFIG['password'],
                                      host=DATABASE_LOCAL_CONFIG['host'],
                                      database=DATABASE_LOCAL_CONFIG['db'])
    cursor = cnx.cursor()
    for cmd in cmd_list:
        if not cmd: continue
        cursor.execute(cmd)
        cnx.commit()


if __name__ == "__main__":
    init_rds_script()