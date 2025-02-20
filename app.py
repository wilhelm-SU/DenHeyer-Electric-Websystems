from urllib import request

from flask import Flask, request, render_template

#notes
#some useful API
#https://docs.python.org/3/library/http.html#module-http
#https://flask.palletsprojects.com/en/stable/api/
app = Flask(__name__)
@app.route('/')
def home():
    return '''
        <h1>DenHeyer Electric</h1>
        <a href="/gallery">Go to Gallery, </a>
        <a href="/reviews">Go to Reviews</a>
    '''
@app.route('/gallery')
def gallery():
    return 'Welcome to the gallery'
    #front end please add a return link in order to return to home

@app.route('/reviews', methods=['GET'])
def reviews():
    return '''
        'Welcome to the reviews, '
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

    return render_template('htmlname.html')
    #front end create HTML file that functions as a form and is called here

if __name__ == '__main__':
    app.run()
