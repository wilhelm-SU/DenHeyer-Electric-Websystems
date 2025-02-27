from urllib import request

from flask import Flask, request, render_template, session, redirect, url_for, jsonify
import psycopg2
from markupsafe import escape #escape is extremely important, must be used on all user submitted arguments to prevent malicious actions

#notes
#some useful API
#https://docs.python.org/3/library/http.html#module-http
#https://flask.palletsprojects.com/en/stable/
#[written by Connor] - this is how to switch between master and main branch in VScode:
#                       git checkout -b master origin/master
#                       git checkout -b main origin/main   


app = Flask(__name__)
app.secret_key = '<KEY>' #placeholder we need to make that key hard to guess and super secret

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
@app.route('/')
def home():
    return '''
        <h1>DenHeyer Electric</h1>
        <a href="/gallery">Go to Gallery </a><br>
        <a href="/reviews">Go to Reviews</a><br>
        <a href="/employeeLogin">Employee Login</a><br>
    '''
@app.route('/gallery')
def gallery():
    return 'Welcome to the gallery'
    #front end please add a return link in order to return to home

@app.route('/reviews', methods=['GET'])
def reviews():
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute("SELECT USERNAME, DESCRIPTION FROM REVIEWS")

        reviewData = cursor.fetchall()

        if not reviewData:
            return jsonify({
                "message": "No reviews available.",
                "write_review_link": "/writeAReview",
                "reviews": []
            })

        review_list = [{"username": row[0], "description": row[1]} for row in reviewData]

        return jsonify({
            "message": "Welcome to the reviews",
            "write_review_link": "/writeAReview",
            "reviews": review_list
        })

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

    #database of reviews would be displayed here
    #front end please add a return link in order to return to home

@app.route('/writeAReview', methods=['GET', 'POST'])
def writeAReview():
    if request.method == 'POST':
        'Please write a review'
        name = request.form['name']
        email = request.form['email']
        review = request.form['review']
        print(name, email, review)
        return 'Thanks for your review'

    return render_template('')
    #front end create HTML file that functions as a form and is called here

@app.route('/requestEstimate', methods=['GET', 'POST'])
def requestEstimate():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        details = request.form['details']

    return render_template('')

@app.route('/employeeLogin', methods=['GET', 'POST'])
def employeeLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == '<USERNAME>' and password == '<PASSWORD>':
            session['loggedIn'] = True
            redirect(url_for('employeePortal'))
        else:
            return 'Invalid username or password'

    return render_template('')
    #front end create HTML file that functions as a login page called here

@app.route('/employeePortal', methods=['GET', 'POST'])
def employeePortal():
    if not session.get('loggedIn'): #extremely important as this prevents non authorized users from accessing pages by simplying writing in url
        return redirect(url_for('employeeLogin'))

    return 'not finished'

@app.route('/logout')
def logout():
    session ['loggedIn'] = False
    return redirect(url_for('employeeLogin'))

if __name__ == '__main__':
    app.run()
