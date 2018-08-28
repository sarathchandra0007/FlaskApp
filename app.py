from flask import Flask,render_template, flash, redirect, session, url_for, logging, request
from data import Articles
# from flask_mysqldb import MySQL
# from flaskext.mysql import MySQL
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)
Articles=Articles()

app.debug=True
connection = sqlite3.connect('data.db',check_same_thread=False)



@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/about')
def new():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html',articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html',id=id)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

class RegisterForm(Form):
    name=StringField('Name',[validators.Length(min=1,max=50)])
    username=StringField('Username',[validators.Length(min=4,max=25)])
    email=StringField('Email',[validators.Length(min=6,max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('conform', message='Passwords do not match')
    ])
    conform = PasswordField('Conform Password')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    print (request.form)
    print (form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create cursor
        cursor = connection.cursor()
        # Execute query
        cursor.execute("INSERT INTO users(name, email, username, password) VALUES(?,?,?,?)", (name, email, username, password))
        connection.commit()
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('new'))
    return render_template('register.html',forminst=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #print (request.form)
        username = request.form['username']
        password_candidate = request.form['password']
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        #print (result)

        if result:
            data = cursor.fetchone()
            #print (data)
            password = data[4]
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run()
