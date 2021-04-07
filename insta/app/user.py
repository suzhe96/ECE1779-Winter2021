from flask import render_template, redirect, flash, url_for, request, current_app
from app import app, db
from app.form import LoginForm, RegistrationForm, ChangePasswordForm, RequestResetPasswordForm, ResetPasswordForm, DeletionForm
from app.models import Users
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from flask_mail import Mail, Message
from threading import Thread
from http import HTTPStatus

import json


@app.route('/user_login', methods=['GET', 'POST'])
def login():
    print("/login add")
    # if user is already logged in, dont not log in until logout
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    form = LoginForm()
    # below if statement check if forms field non empty
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'warning')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main')  # if there is no next page, redirect to main page
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/user_logout')
@login_required
def logout():
    print("/logout add")
    logout_user()
    return redirect(url_for('main'))


def send_async_email(app, msg):
    mail = Mail(app)
    with app.app_context():
        mail.send(msg)


def send_email(recipient, subject, template, **kwargs):
 #   mail = Mail(app)
    msg = Message(
        current_app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender='kevingarnett03@gmail.com',
        recipients=[recipient])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
#    mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    print("/forgotpass add")
    if not current_user.is_anonymous:
        return redirect(url_for('main'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid Email Address]', 'danger')
            return render_template('email_reset_password.html', form=form)
        else:
            token = user.generate_password_reset_token()
            reset_link = url_for('reset_password', token=token, _external=True)
            send_email(
                recipient=user.email,
                subject='Reset Your Password',
                template='forgot_password',
                user=user,
                reset_link=reset_link,
                next=request.args.get('next'))
        flash(
            'A password reset link has been sent to {}.'.format(
                form.email.data), 'info')
        return redirect(url_for('login'))
    return render_template('email_reset_password.html', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    print("/changepass add")
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', "success")
            return redirect(url_for('main'))
        else:
            flash('Original password is invalid/Username is not assigned to you.', 'danger')
    return render_template(
        'change_password.html',
        title='change password',
        form=form,
    )


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    print("/resetpass add")
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email address.', 'danger')
            return redirect(url_for('main'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'success')
            return redirect(url_for('login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'danger')
            return redirect(url_for('main'))
    return render_template(
        'reset_password.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("/register add")
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is not None and user.email == form.email.data:
            flash('The Username Already Existed', 'danger')
            return redirect('register')
        user = Users.query.filter_by(username=form.username.data).first()
        if user is not None and user.username == form.username.data:
            flash('The Email Already Registered', "danger")
            return redirect('register')
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.is_admin = user.username in current_app.config["ADMIN_USER"]
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you Have Successfully Registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/account', methods=['GET'])
def my_account():
    print("/myaccount add")
    return render_template('account.html', title='My_Account')


@app.route('/api/register', methods=['POST'])
def api_register():
    '''
    this is for the project tester usage
    :return:
    '''

    failure_dict = {"success": "false", "error": {"code": HTTPStatus.INTERNAL_SERVER_ERROR, "message": "Register Error!"}}
    success_dict = {"success": "true"}
    data = request.form
    tester_username = request.form['username']
    tester_password = request.form['password']
    if not tester_username or not tester_password:
        failure_dict["error"]["message"]="username or password empty"
        return json.dumps(failure_dict)
    user = Users.query.filter_by(username=tester_username).first()
    if user is not None and user.username == tester_username:
        failure_dict["error"]["message"]="username is already existed"
        return json.dumps(failure_dict)
    user = Users(username=tester_username)
    user.set_password(tester_password)
    user.is_admin = user.username in current_app.config["ADMIN_USER"]
    db.session.add(user)
    db.session.commit()
    return json.dumps(success_dict)

