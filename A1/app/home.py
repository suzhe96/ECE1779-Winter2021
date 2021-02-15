from flask import render_template
from app import a1_webapp


@a1_webapp.route('/')
@a1_webapp.route('/home')
def main():
    return render_template("home.html", title="Home")
