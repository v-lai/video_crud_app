from flask import Flask, request, redirect, url_for, render_template, flash
# from forms import SignupForm, VideoForm
import os
from IPython import embed
import jinja2

app = Flask(__name__)

# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.jinja_env.undefined = jinja2.StrictUndefined
app.jinja_env.auto_reload = True


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=3000,debug=True)