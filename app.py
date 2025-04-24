from flask import Flask
import pytz
from datetime import datetime

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

#HOME Route
from routes.home import (homeBP)
app.register_blueprint(homeBP)

#GALLERY Routes
from routes.gallery import galleryBP
app.register_blueprint(galleryBP)

from routes.galleryManager import galleryManagerBP
app.register_blueprint(galleryManagerBP)

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

from routes.aboutUs import aboutUsBP
app.register_blueprint(aboutUsBP)

from routes.employeeManager import employeeManagerBP
app.register_blueprint(employeeManagerBP)

from routes.galleryManagerManipulation import galleryManagerManipulationBP
app.register_blueprint(galleryManagerManipulationBP)

from routes.employeeSettings import employeeSettingsBP
app.register_blueprint(employeeSettingsBP)

from routes.certifsAndInsurance import certifsAndInsuranceBP
app.register_blueprint(certifsAndInsuranceBP)

if __name__ == '__main__':
    app.run()
