from urllib import request
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, render_template_string
import psycopg2
import pytz
import base64
from markupsafe import escape #escape is extremely important, must be used on all user submitted arguments to prevent malicious actions
from datetime import datetime

from mysql.connector import cursor

#some useful API
#https://docs.python.org/3/library/http.html#module-http
#https://flask.palletsprojects.com/en/stable/
#[written by Connor] - this is how to switch between master and main branch in VScode:
#  for bringing them local        git checkout -b master origin/master
#                                 git checkout -b main origin/main 
#  for when they are local        git checkout master
#                                 git checkout main  

app = Flask(__name__)
app.secret_key = '<KEY>' #placeholder we need to make that key hard to guess and super secret

#Miscellanious Items
###############################################################################################################################################
###############################################################################################################################################

#Time
eastern = pytz.timezone('US/Eastern')
easternTime = datetime.now(eastern)
currentTime = easternTime.strftime('%Y-%m-%d')

#Connect To Database
###############################################################################################################################################
###############################################################################################################################################

host = 'dpg-curuecjv2p9s73aprlvg-a.oregon-postgres.render.com'  # Example: 'localhost' or an IP address
port = '5432'  # Example: '5432'
dbname = 'denheyer_webserver'  # Your database name
user = 'denheyer_webserver_user'  # Your database username
password = 'CEu8cjkwWRcBDCjjZu0GhUBwhHA2Jush'  # Your database password

def connect_to_db():
    return psycopg2.connect(database=dbname, user=user, password=password, host=host, port=port)

try:
    conn = connect_to_db()
    print("Connection successful")
except Exception as e:
    print("Error:", e)

#HOME Routes
###############################################################################################################################################
###############################################################################################################################################

@app.route('/')
def home():
    return render_template('home.html')

#GALLERY Routes
###############################################################################################################################################
###############################################################################################################################################

@app.route('/gallery')
def gallery():

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "PRIMARY_KEY", "IMAGE_DATA", "DESCRIPTION" FROM "GALLERY"')

        print ("Query executed successfully")
        imageData = cursor.fetchall()
        print(imageData)

        image_list = []
        for data in imageData:
            if data[1]:
                base64_imageData = base64.b64encode(data[1]).decode('utf-8')
                image_list.append((data[0], base64_imageData, data[2]))

        print(image_list)

    except Exception as e:
        e = "What just happened?" + str(e)
        return jsonify({'Error': str(e)})
    
    
    
    return '''
        Welcome to the gallery
        <a href="/">Return</a>
        '''

#REVIEW Routes
###############################################################################################################################################
###############################################################################################################################################

@app.route('/reviews', methods=['GET'])
def reviews():
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "DATE"  FROM "REVIEWS" WHERE "PUBLIC" = TRUE')

        print("Query executed successfully")

        reviewData = cursor.fetchall()

        if not reviewData:
            return '''No reviews available.<br>
                      <a href="/writeAReview">Write a review</a>'''

        # Format reviews as templates
        formatted_reviews = "<br><br>".join([f"<strong>Name:</strong> {row[0]}<br><strong>Description:</strong> {row[1]} <br><strong>Date:</strong> {row[2]}" for row in reviewData])

        return f'''<h2>Welcome to the reviews</h2>
                   {formatted_reviews}
                   <br><br>
                   <a href="/writeAReview">Write a review</a><br>
                   <a href="/">Return</a>''', 200

        
    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            # Optionally log any errors related to closing
            print(f"Error closing connection: {e}")

@app.route('/writeAReview', methods=['GET', 'POST'])
def writeAReview():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        review = request.form.get('review')
        date = currentTime

        if not name or not email or not review:
            return "All fields are required.", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('INSERT INTO "REVIEWS" ("NAME", "EMAIL", "DESCRIPTION", "DATE") VALUES (%s, %s, %s, %s)',
                           (name, email, review, date))
            connect.commit()


            return '''
            Thanks for your review!<br>
            <a href="/">Return</a>
        
            '''

        except Exception as e:
            return jsonify({'Error': str(e)})

        finally:
            try:
                if cursor:
                    cursor.close()
                if connect:
                    connect.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

    # Render the templates form from templates folder
    return render_template('submitReviewForm.html')

#ESTIMATE Routes
###############################################################################################################################################
###############################################################################################################################################

@app.route('/requestEstimate', methods=['GET', 'POST'])
def requestEstimate():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        details = request.form['details']

    return render_template('')

#EMPLOYEE Routes
###############################################################################################################################################
###############################################################################################################################################

@app.route('/employeeLogin', methods=['GET', 'POST'])
def employeeLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "Both fields are required.", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            # Check if credentials exist in the database
            cursor.execute('SELECT * FROM "EMPLOYEE_CREDENTIALS" WHERE "EMPLOYEE_USERNAME" = %s AND "EMPLOYEE_PASSWORD" = %s', 
                           (username, password))
            employee = cursor.fetchone()

            if employee:
                session['loggedIn'] = True
                session['username'] = username
                return redirect(url_for('employeePortal'))  # Redirect to the employee portal
            else:
                return ('''Invalid credentials. Please try again.<br>
                        "<a href="/employeeLogin">Return</a><br>''', 401)

        except Exception as e:
            return jsonify({'Error': str(e)})

        finally:
            try:
                if cursor:
                    cursor.close()
                if connect:
                    connect.close()
            except Exception as e:
                print(f"Error closing connection: {e}")

    # Render login form
    return render_template('employeeLoginForm.html')

@app.route('/employeePortal')
def employeePortal():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employeeLogin'))

    username = session.get('username')
    return render_template('employeePortal.html', username=username)

@app.route('/reviewManager', methods=['GET', 'POST'])
def reviewManager():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simply writing in url
        return redirect(url_for('employeeLogin'))

    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "NAME", "DESCRIPTION", "EMAIL", "DATE", "PUBLIC", "PRIMARY_KEY" FROM "REVIEWS"')

        print("Query executed successfully")

        reviewData = cursor.fetchall()

        if not reviewData:
            return '''No reviews available.<br>'''

        # Format reviews as templates
        formatted_reviews = "<br><br>".join(
            [f"""
            <strong>Date:</strong> {row[3]}<br><br>
            <strong>Name:</strong> {row[0]}<br>
            <strong>Description:</strong> {row[1]}<br>
            <strong>Email:</strong> {row[2]}<br>
            <strong>Publicly displayed:</strong> {row[4]}
            <form action="/togglePublic/{row[5]}" method="POST">
                <button type="submit">
                    {'Set to Private' if row[4] else 'Set to Public'}
                </button>
        </form> 
        """ for row in reviewData])

        return f'''<h2>Welcome to the review manager</h2>
                    Here you can accept or reject reviews here.<br><br>
                   {formatted_reviews}
                   <br><br>
                   <a href="/employeePortal">Return</a>''', 200

    except Exception as e:
        return jsonify({'Error': str(e)})

    finally:
        try:
            if cursor:
                cursor.close()
            if connect:
                connect.close()
        except Exception as e:
            # Optionally log any errors related to closing
            print(f"Error closing connection: {e}")

@app.route('/togglePublic/<key>', methods=['POST'])
def togglePublic(key):
    connect = connect_to_db()
    cursor = connect.cursor()

    cursor.execute('SELECT "PUBLIC" FROM "REVIEWS" WHERE "PRIMARY_KEY" = %s', (key,))
    currentStatus = cursor.fetchone()[0]
    newStatus = not currentStatus

    cursor.execute('UPDATE "REVIEWS" SET "PUBLIC" = %s WHERE "PRIMARY_KEY" = %s', (newStatus, key))

    connect.commit()

    return redirect(url_for('reviewManager'))

@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employeeLogin'))
    return ''

@app.route('/logout')
def logout():
    session ['loggedIn'] = False
    return redirect(url_for('employeeLogin'))


if __name__ == '__main__':
    app.run()
