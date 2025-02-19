from flask import Flask

app = Flask(__name__)


@app.route('/')
def denheyerElectric():  # put application's code here
    return 'DenHeyer Electric'


if __name__ == '__main__':
    app.run()
