from urllib import request

from flask import Flask, request, render_template, session
from markupsafe import escape #escape is extremely important, must be used on all user submitted arguments to prevent malicious actions

#notes
#some useful API
#https://docs.python.org/3/library/http.html#module-http
#https://flask.palletsprojects.com/en/stable/
app = Flask(__name__)
app.secret_key = '<KEY>' #placeholder we need to make that key hard to guess and super secret
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
    return '''
        Welcome to the reviews<br>
        <a href="/writeAReview">Write a review!</a>
    '''
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
