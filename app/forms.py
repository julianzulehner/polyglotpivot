from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import Email, Length, DataRequired, EqualTo, ValidationError
from app.models import User
from app import db
import sqlalchemy as sa


class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField("Password",validators=[DataRequired(), Length(min=8, max=30)])
    email = StringField("Email",validators=[DataRequired(),Email()])
    confirm = PasswordField("Password",validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(max=140)])
    submit = SubmitField("Submit")
    languages = SelectMultipleField("Languages")

class AddPostForm(FlaskForm):
    post = TextAreaField("New Post",validators=[Length(max=500), DataRequired()])
    submit = SubmitField("Submit")