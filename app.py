from flask import Flask,render_template, flash, redirect, session, url_for, logging, request
#from data import Articles
# from flask_mysqldb import MySQL
# from flaskext.mysql import MySQL
import sqlite3
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
#Articles=Articles()

app.debug=True
connection = sqlite3.connect('data.db',check_same_thread=False)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/about')
def new():
    return render_template('about.html')

@app.route('/articles')
def articles():
    cursor = connection.cursor()
    connection.row_factory = dict_factory
    result = cursor.execute("SELECT * FROM flask_articles")
    articles = cursor.fetchall()
    if result:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    cursor.close()

    return render_template('articles.html',articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    cursor = connection.cursor()
    connection.row_factory = dict_factory
    result = cursor.execute("SELECT * FROM flask_articles WHERE id = ?", (id,))
    article = cursor.fetchone()
    cursor.close()
    return render_template('article.html', article=article)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/dashboard')
@is_logged_in
def dashboard():
    cursor = connection.cursor()
    connection.row_factory = dict_factory
    result = cursor.execute("SELECT * FROM flask_articles")
    articles = cursor.fetchall()
    if result:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    cursor.close()

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
    #print (request.form)
    #print (form)
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
                session['logged_in'] = True
                session['username'] = username
                #print (session)
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
@is_logged_in
def logout():
    session.clear()
    flash("Logged out successfully",'success')
    return redirect(url_for('login'))

#Articles
class ArticleForm(Form):
    title=StringField('Title',[validators.Length(min=1,max=90)])
    body=TextAreaField('Body',[validators.Length(min=5)])

@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        cursor = connection.cursor()
        # Execute query
        cursor.execute("INSERT INTO flask_articles(title,body,author) VALUES(?,?,?)", (title,body,session['username']))
        connection.commit()
        cursor.close()
        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('aricle_form.html',form=form)


@app.route('/article_edit/<string:id>',methods=['GET','POST'])
def edit_article(id):
    cursor = connection.cursor()
    connection.row_factory = dict_factory
    result = cursor.execute("SELECT * FROM flask_articles WHERE id = ?", (id,))
    article = cursor.fetchone()
    #print(article[1])
    form = ArticleForm(request.form)
    form.title.data = article["title"]
    form.body.data = article["body"]

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        cursor.execute ("UPDATE flask_articles SET title=?, body=? WHERE id=?",(title, body, id))
        connection.commit()
        cursor.close()
        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run()
