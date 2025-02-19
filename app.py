from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <h1>DenHeyer Electric</h1>
        <a href="/gallery">Go to Gallery</a>
    '''
@app.route('/gallery')
def gallery():
    return 'Welcome to the gallery'
    #front end please add a return link in order to return to home


if __name__ == '__main__':
    app.run()
