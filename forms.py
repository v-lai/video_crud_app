from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, validators

class SignupForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3)])
    email = StringField('E-mail', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

# class VideoForm(FlaskForm):
#     video = StringField('Video Link', [validators.Length(min=10, max=50)])
#     favorite = BooleanField('Favorite!')