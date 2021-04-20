import uuid
import boto3
import time
from threading import Thread

AWS_S3_BUCKET_BGP = "s3lambdazhev2"

def bgp_cb():
    while True:
        time.sleep(120)
        print("s3 trigger...")
        s3 = boto3.resource('s3', region_name='us-east-1')
        content = str(uuid.uuid1())
        filename = "{}.txt".format(content)
        s3.Object(AWS_S3_BUCKET_BGP, filename).put(Body=content)

def main():
    bgp = Thread(target=bgp_cb)
    bgp.daemon = True
    bgp.start()
    print("Zombie users cleaning thread has been started")


if __name__ == "__main__":
    bgp_cb()