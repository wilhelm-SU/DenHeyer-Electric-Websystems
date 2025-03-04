from urllib import request

from flask import Flask, request, render_template, session, redirect, url_for, jsonify, render_template_string
import psycopg2
from markupsafe import escape #escape is extremely important, must be used on all user submitted arguments to prevent malicious actions

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

#Routes
###############################################################################################################################################
###############################################################################################################################################

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
    return '''
        Welcome to the gallery
        <a href="/">Return</a>
        '''

@app.route('/reviews', methods=['GET'])
def reviews():
    try:
        connect = connect_to_db()
        cursor = connect.cursor()
        cursor.execute('SELECT "USERNAME", "DESCRIPTION" FROM "REVIEWS"')

        print("Query executed successfully")

        reviewData = cursor.fetchall()

        if not reviewData:
            return '''No reviews available.<br>
                      <a href="/writeAReview">Write a review</a>'''

        # Format reviews as templates
        formatted_reviews = "<br><br>".join([f"<strong>Username:</strong> {row[0]}<br><strong>Description:</strong> {row[1]}" for row in reviewData])

        return f'''<h2>Welcome to the reviews</h2>
                   {formatted_reviews}
                   <br><br>
                   <a href="/writeAReview">Write a review</a><br>
                   <a href="/">Return</a>''', 200

        '''This stuff below is to Format reviews as plain text'''
        # if not reviewData:
        #     return "No reviews available.\nWrite a review: /writeAReview"

        # # Format each review as plain text with spacing
        # formatted_reviews = "\n\n".join([f"Username: {row[0]}\nDescription: {row[1]}" for row in reviewData])

        # return f"Welcome to the reviews\n\n{formatted_reviews}\n\nWrite a review: /writeAReview", 200, {"Content-Type": "text/plain"}

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

    #front end please add a return link in order to return to home

@app.route('/writeAReview', methods=['GET', 'POST'])
def writeAReview():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        review = request.form.get('review')

        if not name or not email or not review:
            return "All fields are required.", 400

        try:
            connect = connect_to_db()
            cursor = connect.cursor()

            cursor.execute('INSERT INTO "REVIEWS" ("USERNAME", "EMAIL", "DESCRIPTION") VALUES (%s, %s, %s)', 
                           (name, email, review))
            connect.commit()

            return "Thanks for your review!"

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

    return render_template('employeeLoginForm.html')
    #front end please access this HTML file in templates directory and make it a form -J

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
