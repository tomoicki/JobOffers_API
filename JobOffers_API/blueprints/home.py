from flask import Blueprint, render_template

home = Blueprint('home', __name__)


@home.route('/')
def welcome():
    return render_template('home.html', title='Welcome!')
