from urllib import request
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, render_template_string
import psycopg2
import pytz
import base64
from markupsafe import escape #escape is extremely important, must be used on all user submitted arguments to prevent malicious actions
from datetime import datetime
from mysql.connector import cursor

#[written by Connor] - this is how to switch between master and main branch in VScode:
#  for bringing them local        git checkout -b master origin/master
#                                 git checkout -b main origin/main 
#  for when they are local        git checkout master
#                                 git checkout main  

# python -m flask run


app = Flask(__name__)
app.secret_key = '<KEY>' #placeholder we need to make that key hard to guess and super secret

#Time
eastern = pytz.timezone('US/Eastern')
easternTime = datetime.now(eastern)
currentTime = easternTime.strftime('%Y-%m-%d %H:%M:%S')

#Connect To Database
from databaseModule import connect_to_db

#HOME Route
from routes.home import (homeBP)
app.register_blueprint(homeBP)

#GALLERY Route
from routes.gallery import galleryBP
app.register_blueprint(galleryBP)

#REVIEW Routes
from routes.review import reviewBP
app.register_blueprint(reviewBP)

#ESTIMATE Routes
from routes.estimate import estimateBP
app.register_blueprint(estimateBP)

#EMPLOYEE Routes
from routes.employee import employeeBP
app.register_blueprint(employeeBP)

from routes.estimateManager import estimateManagerBP
app.register_blueprint(estimateManagerBP)

from routes.reviewManager import reviewManagerBP

app.register_blueprint(reviewManagerBP)

if __name__ == '__main__':
    app.run()
