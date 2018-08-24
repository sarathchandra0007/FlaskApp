from flask import Flask,render_template

app = Flask(__name__)

app.debug=True

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/new')
def new():
    return 'new page'

if __name__ == '__main__':
    app.run()
