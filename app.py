from flask import Flask, request, redirect, url_for, render_template, flash, session
from forms import SignupForm, LoginForm, VideoForm
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
    videos = db.relationship('Video', backref='user', lazy='dynamic')

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
    return render_template('/users/index.html', users=User.query.all())

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('profile'))
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('/users/signup.html', form=form)
        newuser = User(request.form['username'], request.form['email'], request.form['password'])
        user_u = User.query.filter_by(username=request.form['username']).first()
        user_e = User.query.filter_by(email=request.form['email']).first()
        if user_u:
            flash('That username is already taken. Please try another username.')
            return render_template('/users/signup.html', form=form)
        if user_e:
            flash('That email has already been used. Please use a different email.')
            return render_template('/users/signup.html', form=form)
        db.session.add(newuser)
        db.session.commit()
        session['username'] = newuser.username
        flash('Thanks for signing up!')
        return redirect(url_for('profile'))
    return render_template('/users/signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if 'username' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('/users/login.html', form=form)
        user = User.query.filter_by(username=request.form['username']).first()
        if not user or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return render_template('/users/login.html', form=form)
        session['username'] = form.username.data
        flash('Welcome back!')
        return redirect(url_for('profile', id=user.id))
    return render_template('/users/login.html', form=form)

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
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first_or_404()
    if user is None:
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

    return render_template('/users/profile.html', id=id, user=user, users=User.query.all())

@app.route('/profile/<int:id>/edit', methods=['GET', 'POST'])
def edit_profile(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first_or_404()
    if user is None:
        return redirect(url_for('login'))

    form = SignupForm(obj=user)
    form.populate_obj(user)
    if request.method == 'POST' and form.validate():
        db.session.add(user)
        db.session.commit()
        flash("Edited user!")
        return redirect(url_for('logout'))
    return render_template('/users/edit.html', id=id, user=user, users=User.query.all(), form=form)


class Video(db.Model):
    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    video = db.Column(db.VARCHAR(50))
    confirm = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, video, confirm, user_id):
        self.video = video
        self.confirm = confirm
        self.user_id = user_id

    def __repr__(self):
        return "{}, user_id: {}, video: {}, confirm: {}".format(self.user.username, self.user_id, self.video, self.confirm)

@app.route('/profile/<int:id>/videos')
def v_index(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first_or_404()
    if user is None:
        return redirect(url_for('login'))

    check_user = User.query.filter_by(id=id).first_or_404()
    return render_template('/videos/index.html', id=check_user.id, users=User.query.all(), videos=check_user.videos)

@app.route('/profile/<int:id>/videos/new', methods=['GET', 'POST'])
def v_new(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first_or_404()
    if user is None:
        return redirect(url_for('login'))

    check_user = User.query.filter_by(id=id).first_or_404()
    vform = VideoForm(request.form)
    if request.method == 'POST' and vform.validate():
        # embed()
        if request.form['confirm'] == False:
            flash("You must confirm before submitting!")
            return render_template('/videos/new.html', id=check_user.id, users=User.query.all(), form=vform)
        check_confirm = True
        db.session.add(Video(request.form['video'], check_confirm, id))
        db.session.commit()
        flash("New video posted!")
        return redirect(url_for('v_index', id=check_user.id, users=User.query.all(), videos=check_user.videos))
    return render_template('/videos/new.html', id=check_user.id, users=User.query.all(), form=vform)


@app.route('/profile/<int:id>/videos/<int:vid>', methods=["GET", "PATCH", "DELETE"])
def v_show(id, vid):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first_or_404()
    if user is None:
        return redirect(url_for('login'))

    check_user = User.query.filter_by(id=id).first_or_404()
    check_video = Video.query.filter_by(id=vid).first_or_404()
    if request.method == b"PATCH":
        check_video.video = request.form['video']
        db.session.add(check_video)
        db.session.commit()
        flash("Video edited!")
        return redirect(url_for('v_index', id=check_user.id, users=User.query.all(), videos=check_user.videos))

    if request.method == b"DELETE":
        db.session.delete(check_video)
        db.session.commit()
        flash("Video deleted!")
        return redirect(url_for('v_index', id=check_user.id, users=User.query.all(), videos=check_user.videos))

    return render_template('/videos/show.html', id=check_user.id, users=User.query.all(), video=check_video, vid=vid)


@app.route('/profile/<int:id>/videos/<int:vid>/edit', methods=['GET', 'POST'])
def v_edit(id, vid):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first_or_404()
    if user is None:
        return redirect(url_for('login'))

    check_user = User.query.filter_by(id=id).first_or_404()
    check_video = Video.query.filter_by(id=vid).first_or_404()
    
    vform = VideoForm(obj=check_video)
    vform.populate_obj(check_video)
    if request.method == 'POST' and vform.validate():
        db.session.add(check_video)
        db.session.commit()
        flash("Edited video!")
        return redirect(url_for('v_index', id=check_user.id, users=User.query.all(), videos=check_user.videos))
    return render_template('/videos/edit.html', id=check_user.id, users=User.query.all(), user=check_user, video=check_video, form=vform)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
