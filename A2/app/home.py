from flask import render_template, flash, url_for, redirect
import time
from app import a2
from app import awsworker
from app import awsconfig
from app.form import AutoScalarForm
from app import autoscaler
from app import awshandler

@a2.route('/')
@a2.route('/home', methods=['POST', 'GET'])
def main():

    #TODO: display worker list based on worker_dict
    #      display another attribute on healthy count (since it is out of sync mostly)

    awsworker.update_aws_worker_dict()
    healthy_workers = awsworker.get_ec2_workers_chart()
    current_total_workers = len(awsworker.get_aws_worker_dict())
    worker_dict = awsworker.get_aws_worker_dict()
    pending_workers = 0
    stopping_workers = 0
    running_workers = 0
    for worker in worker_dict:
        if worker_dict[worker] == awsconfig.AWS_EC2_STATUS_PENDING:
            pending_workers = pending_workers+ 1
        elif worker_dict[worker] == awsconfig.AWS_EC2_STATUS_STOPPING:
            stopping_workers = stopping_workers + 1
        elif worker_dict[worker] == awsconfig.AWS_EC2_STATUS_RUNNING:
            running_workers = running_workers + 1
#    print("[HOME]worker list size: {}".format(len(healthy_workers[1])))
    return render_template("home.html", title="Home", worker_number=healthy_workers,current_total_workers = current_total_workers, pending_workers=pending_workers, stopping_workers=stopping_workers, running_workers = running_workers)


@a2.route('/get_workers_list', methods=['POST', 'GET'])
def get_workers_list():
#  time_stamps = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
#   cpu_stats = [10,20,30,80,50,70,10,20,30,80,50,70]
#   cpu_util = {}
#   http_requests = [100,400,600,700,800,900]
#   HTTP_Req = {}
#   for x in range(8):
#        cpu_util[x] = [time_stamps, cpu_stats]
#        if x == 2:
#            http_requests = [100,200,300,400,500,600,700,800]
#        HTTP_Req[x] = [time_stamps, http_requests]

    #TODO: for each worker, display its current status getting from worker_dict
    #ADDED current status for each worker, remove above TODO after check

    awsworker.update_aws_worker_dict()
    worker_dict = awsworker.get_aws_worker_dict()
    cpu_util = awsworker.get_all_ec2_cpu_utilizaton(worker_dict)
    http_req = awsworker.get_all_workers_http_request(worker_dict)
    worker_status = {}
    worker_index = 0;
    worker_instance_id = {}
    for worker in worker_dict:
        worker_status[worker_index]=worker_dict[worker]
        worker_instance_id[worker_index]=worker
        worker_index = worker_index + 1
    print("[WROKER_LIST]cpu dict size: {}, http dict size: {}".format(len(cpu_util), len(http_req)))
    return render_template("get_workers_list.html", title="Listing_Workers", CPU_Util = cpu_util, HTTP_Req=http_req, worker_status=worker_status, worker_instance_id=worker_instance_id)


@a2.route('/load_balancer', methods=['POST', 'GET'])
def load_balancer():
    awsworker.update_aws_worker_dict()
    DNS = awsworker.get_elb_dns()
    return render_template("load_balancer.html", title="Load_Balancer", DNS = DNS)


@a2.route('/configure_worker_pool', methods=['POST', 'GET'])
def configure_worker_pool():
    return render_template("configure_worker_pool.html", title="Configure_Worker_Pool")


@a2.route('/increase_worker_pool', methods=['POST', 'GET'])
def increase_worker_pool():
    awsworker.update_aws_worker_dict()
    return_value = awsworker.scaling_instance(awsconfig.AWS_EC2_SCALING_UP, 1)
    if return_value == awsconfig.AWS_ERROR_EC2_NUM_EXCEED_MAX:
        flash('Increase Worker Pool Failed: {}'.format(awsconfig.AWS_ERROR_MSG[return_value]), 'danger')
    elif return_value == awsconfig.AWS_ERROR_EC2_NUM_SCALE_ZERO:
        flash('Increase Worker Pool: Exist pending workers', 'success')
    else:
        flash('Increase Worker Pool Successfully', 'success')
    return redirect(url_for('configure_worker_pool'))


@a2.route('/decrease_worker_pool', methods=['POST', 'GET'])
def decrease_worker_pool():
    awsworker.update_aws_worker_dict()
    return_value = awsworker.scaling_instance(awsconfig.AWS_EC2_SCALING_DOWN, 1)
    if return_value == awsconfig.AWS_ERROR_EC2_NUM_BELOW_MIN:
        flash('Decrease Worker Pool Failed: {}'.format(awsconfig.AWS_ERROR_MSG[return_value]), 'danger')
    elif return_value == awsconfig.AWS_ERROR_EC2_NUM_SCALE_ZERO:
        flash('Decrease Worker Pool: Exist stopping workers', 'success')
    else:
        flash('Decrease Worker Pool Successfully', 'success')
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
    awsworker.stop_all()
    flash('Stopped all EC2 instances Successfully', 'success')
    return render_template("termination.html", title="Home")


@a2.route('/delete_data', methods=['POST', 'GET'])
def delete_data():
    s3_handler = awshandler.get_s3()
    delete_s3_data(s3_handler)
    # awsworker.init_rdb()
    flash('Deleted all data Successfully', 'success')
    return redirect(url_for('main'))


def delete_s3_data(s3_handler):
    for key in s3_handler.list_objects(Bucket='a1db')['Contents']:
            s3_handler.delete_objects(
                Bucket='a1db',
                Delete={
                    'Objects': [
                        {
                            'Key': key['Key'],
                        },
                    ],
                    'Quiet': True
                },
            )
