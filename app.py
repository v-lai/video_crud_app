from flask import Flask, request, redirect, url_for, render_template, flash, session
from forms import SignupForm, LoginForm #, VideoForm
from flask_modus import Modus
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
    return render_template('index.html', users=User.query.all())

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('profile'))
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('signup.html', form=form)
        newuser = User(request.form['username'], request.form['email'], request.form['password'])
        user_u = User.query.filter_by(username=request.form['username']).first()
        user_e = User.query.filter_by(email=request.form['email']).first()
        if user_u:
            flash('That username is already taken. Please try another username.')
            return render_template('signup.html', form=form)
        if user_e:
            flash('That email has already been used. Please use a different email.')
            return render_template('signup.html', form=form)
        db.session.add(newuser)
        db.session.commit()
        session['username'] = newuser.username
        flash('Thanks for signing up!')
        return redirect(url_for('profile'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if 'username' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('login.html', form=form)
        user = User.query.filter_by(username=request.form['username']).first()
        if not user or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return render_template('login.html', form=form)
        session['username'] = form.username.data
        flash('Welcome back!')
        return redirect(url_for('profile', id=user.id))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'username' not in session:
        flash('Please login.')
        return redirect(url_for('login'))
    session.pop('username', None)
    flash('You have logged out.')
    return redirect(url_for('index'))

@app.route('/profile/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def profile(id):
    user = User.query.filter_by(username=session['username']).first_or_404()
    if 'username' not in session or user is None:
        return redirect(url_for('login'))

    # embed()
    if request.method == b"PATCH":
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.add(user)
        db.session.commit()
        flash("Edited user!")
        return redirect(url_for('logout'))

    if request.method == b"DELETE":
        session.pop('username', None)
        db.session.delete(id)
        db.session.commit()
        flash("User deleted!")
        return redirect(url_for('index'))

    return render_template('profile.html', id=id, user=user, users=User.query.all())

@app.route('/profile/<int:id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    user = User.query.filter_by(username=session['username']).first_or_404()
    if 'username' not in session or user is None:
        return redirect(url_for('login'))

    form = SignupForm(obj=user)
    form.populate_obj(user)
    if request.method == 'POST' and form.validate():
        db.session.add(user)
        db.session.commit()
        flash("Edited user!")
        return redirect(url_for('logout'))
    return render_template('edit.html', id=id, user=user, users=User.query.all(), form=form)


if __name__ == '__main__':
    app.run(port=3000, debug=True)
