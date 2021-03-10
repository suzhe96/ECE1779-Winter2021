from flask import render_template
from app import a2


@a2.route('/')
@a2.route('/home')

def main():
    return render_template("home.html", title="Home")
