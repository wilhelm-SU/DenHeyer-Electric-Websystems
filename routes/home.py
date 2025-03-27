from flask import Blueprint, render_template

homeBP = Blueprint('home', __name__)

@homeBP.route('/')
def home():
    return render_template('home.html')