from flask import render_template, flash, url_for, redirect
import time
from app import a2
from app import awsworker
from app import awsconfig
from app.form import AutoScalarForm
from app import autoscaler

@a2.route('/')
@a2.route('/home', methods=['POST', 'GET'])
def main():
    time_stamps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    worker_numbers = [10, 20, 30, 80, 50, 70, 10, 20, 30, 80, 50, 70]
    Workers = [time_stamps, worker_numbers]

 #   while True:
 #       awsworker.update_aws_worker_dict()
 #       worker_dict = awsworker.get_aws_worker_dict()
 #       for key in worker_dict:
 #           if worker_dict[key] == awsconfig.AWS_EC2_STATUS_RUNNING:
 #               return render_template("home.html", title="Home", worker_number=Workers)
 #       time.sleep(30)
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
   return render_template("get_workers_list.html", title="Listing_Workers", CPU_Util = cpu_util, HTTP_Req=HTTP_Req)


@a2.route('/load_balancer', methods=['POST', 'GET'])
def load_balancer():
    return render_template("load_balancer.html", title="Load_Balancer")


@a2.route('/configure_worker_pool', methods=['POST', 'GET'])
def configure_worker_pool():
    return render_template("configure_worker_pool.html", title="Configure_Worker_Pool")


@a2.route('/increase_worker_pool', methods=['POST', 'GET'])
def increase_worker_pool():
    flash('Increased Worker Pool Successfully', 'success')
    return redirect(url_for('configure_worker_pool'))


@a2.route('/decrease_worker_pool', methods=['POST', 'GET'])
def decrease_worker_pool():
    flash('Decreased Worker Pool Successfully', 'success')
    return redirect(url_for('configure_worker_pool'))


@a2.route('/configure_auto_scaler', methods=['POST', 'GET'])
def configure_auto_scaler():
    form = AutoScalarForm()
    if form.validate_on_submit():
        current_auto_scalar_policy = autoscaler.auto_scaler_policy_get()
        cpu_threshold_grow = form.cpu_threshold_grow.data
        cpu_threshold_shrink = form.cpu_threshold_shrink.data
        expand_ratio = form.expand_ratio.data
        shrink_ratio = form.shrink_ratio.data
        if cpu_threshold_grow == None:
            cpu_threshold_grow = current_auto_scalar_policy['cpu_grow_threshold']
        if cpu_threshold_shrink == None:
            cpu_threshold_shrink = current_auto_scalar_policy['cpu_shrink_threshold']
        if expand_ratio == None:
            expand_ratio = current_auto_scalar_policy['cpu_grow_ratio']
        if shrink_ratio == None:
            shrink_ratio = current_auto_scalar_policy['cpu_shrink_ratio']
        if cpu_threshold_shrink >= cpu_threshold_grow:
            flash('Configure Auto Scalar Policy Failed. CPU Threshold Grow Should not be Larger then CPU Threshold Shrink', 'danger')
        else:
            flash('Configure Auto Scalar Policy Successfully', 'success')
            autoscaler.auto_scaler_policy_set(cpu_threshold_grow, cpu_threshold_shrink, expand_ratio, shrink_ratio)
        print("The cpu_threshold_grow is {}, cpu_threshold_shrink is {}, expand_ratio is {}, shrink_ratio is {}".format(cpu_threshold_grow, cpu_threshold_shrink, expand_ratio, shrink_ratio))
        return redirect(url_for('configure_auto_scaler'))
    return render_template('configure_auto_scaler.html', title="configure_auto_scalar", form=form)


@a2.route('/stop', methods=['POST', 'GET'])
def stop():
    flash('Stopped all EC2 instances Successfully', 'success')
    return render_template("termination.html", title="Home")


@a2.route('/delete_data', methods=['POST', 'GET'])
def delete_data():
    flash('Deleted all data Successfully', 'success')
    return redirect(url_for('main'))
