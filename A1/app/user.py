from flask import render_template
from app import a1_webapp
from app.form import LoginForm


@a1_webapp.route('/user_login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login Requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('main'))
    return render_template('login.html', title='Sign In', form=form)
