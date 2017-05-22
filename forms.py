from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField, validators

class SignupForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3)])
    email = StringField('E-mail', [validators.Length(min=6, max=35), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        return True

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Required("Please enter your username.")])
    password = PasswordField('Password', [validators.Required("Please enter your password.")])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        return True

class VideoForm(FlaskForm):
    video = StringField('Video Link', [validators.Length(min=10, max=50)])
    confirm = BooleanField('Confirm')
    
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        return True
