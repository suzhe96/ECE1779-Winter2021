from flask import render_template, flash
import time
from app import a2
from app import awsworker
from app import awsconfig

# Initalize the first worker
awsworker.initialize_first_worker()

@a2.route('/')
@a2.route('/home')
def main():
    time_stamps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    worker_numbers = [10, 20, 30, 80, 50, 70, 10, 20, 30, 80, 50, 70]
    Workers = [time_stamps, worker_numbers]

    while true:
        awsworker.update_aws_worker_dict()
        worker_dict = get_aws_worker_dict()
        for key in worker_dict:
            if worker_dict[key] == awsconfig.AWS_EC2_STATUS_RUNNING:
                return render_template("home.html", title="Home", worker_number=Workers)
        time.sleep(30)
    return render_template("home.html", title="Home", worker_number=Workers)


@a2.route('/get_workers_list')
def get_workers_list():
   time_stamps = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
   cpu_stats = [10,20,30,80,50,70,10,20,30,80,50,70]
   cpu_util = {}
   http_requests = [100,400,600,700,800,900]
   HTTP_Req = {}
   for x in range(8):
        cpu_util[x] = [time_stamps, cpu_stats]
        if x == 2:
            http_requests = [100,200,300,400,500,600,700,800]
        HTTP_Req[x] = [time_stamps, http_requests]
   return render_template("get_workers_list.html", title="Listing_Workers", CPU_Util = cpu_util, HTTP_Req = HTTP_Req)


@a2.route('/load_balancer')
def load_balancer():
    return render_template("load_balancer.html", title="Home")


@a2.route('/configure_worker_pool')
def configure_worker_pool():
    return render_template("configure_worker_pool.html", title="Home")


@a2.route('/increase_worker_pool')
def increase_worker_pool():
    flash('Increased Worker Pool Successfully')
    return


@a2.route('/decrease_worker_pool')
def decrease_worker_pool():
    flash('Decreased Worker Pool Successfully')
    return


@a2.route('/configure_auto_scaler')
def configure_auto_scaler():
    return render_template("configure_auto_scaler.html", title="Home")
@a2.route('/stop')
def stop():
    return render_template("stop.html", title="Home")
@a2.route('/delete_data')
def delete_data():
    return render_template("delete_data.html", title="Home")
