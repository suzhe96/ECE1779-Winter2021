from flask import render_template, flash, redirect, url_for, request
from app import a2


@a2.route('/')
@a2.route('/home', methods=['POST', 'GET'])
def main():
    time_stamps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    worker_numbers = [10, 20, 30, 80, 50, 70, 10, 20, 30, 80, 50, 70]
    Workers = [time_stamps, worker_numbers]
    return render_template("home.html", title="Home", worker_number=Workers)


@a2.route('/get_workers_list', methods=['POST', 'GET'])
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


@a2.route('/load_balancer', methods=['POST', 'GET'])
def load_balancer():
    return render_template("load_balancer.html", title="Home")


@a2.route('/configure_worker_pool', methods=['POST', 'GET'])
def configure_worker_pool():
    return render_template("configure_worker_pool.html", title="Home")


@a2.route('/increase_worker_pool' ,methods=['POST', 'GET'])
def increase_worker_pool():
    flash('Increased Worker Pool Successfully', 'success')
    return redirect(url_for('configure_worker_pool'))


@a2.route('/decrease_worker_pool' ,methods=['POST', 'GET'])
def decrease_worker_pool():
    flash('Decreased Worker Pool Successfully', 'success')
    return redirect(url_for('configure_worker_pool'))


@a2.route('/configure_auto_scaler', methods=['POST', 'GET'])
def configure_auto_scaler():
    return render_template("configure_auto_scaler.html", title="Home")


@a2.route('/stop', methods=['POST', 'GET'])
def stop():
    flash('Stopped all EC2 instances Successfully', 'success')
    return render_template("termination.html", title="Home")


@a2.route('/delete_data', methods=['POST', 'GET'])
def delete_data():
    flash('Deleted all data Successfully', 'success')
    return redirect(url_for('main'))
