from flask import Flask
from dotenv import load_dotenv
from databaseModule import connect_to_db
import pytz
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret" )

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

from routes.FAQ import FAQBP
app.register_blueprint(FAQBP)

@app.route('/test-db')
def test_db():
    conn = connect_to_db()
    if conn is None:
        return "DB connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees LIMIT 1")  # example table
        result = cursor.fetchall()
        return str(result)
    except Exception as e:
        # Print full error to logs
        print("DB query failed:", e)
        return f"DB query failed: {e}", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


#if __name__ == '__main__':
#    app.run()
