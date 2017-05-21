from flask import Flask, request, redirect, url_for, render_template, flash, session
from forms import SignupForm, LoginForm #, VideoForm
import os

# for models
from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

from IPython import embed
import jinja2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/flask-video-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.jinja_env.undefined = jinja2.StrictUndefined
app.jinja_env.auto_reload = True

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    email = db.Column(db.Text, unique=True)
    pwdhash = db.Column(db.Text)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def __repr__(self):
        return "username: {}, email: {}".format(self.username, self.email)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('signup.html', form=form)
        newuser = User(request.form['username'], request.form['email'], request.form['password'])
        db.session.add(newuser)
        db.session.commit()
        session['username'] = newuser.username
        flash('Thanks for signing up!')
        return redirect(url_for('profile'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('login.html', form=form)
        session['username'] = form.username.data
        flash('Welcome back!')
        return redirect(url_for('profile'))
    return render_template('login.html', form=form)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username = session['username']).first()
    
    if user is None:
        return redirect(url_for('login'))
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(port=3000,debug=True)