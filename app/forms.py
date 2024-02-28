from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField, SelectField
from wtforms.validators import Email, Length, DataRequired, EqualTo, ValidationError, NoneOf
from app.models import User
from app import db
import sqlalchemy as sa
from wtforms.widgets import ListWidget, TableWidget, CheckboxInput, TextArea

class NotEqualTo:
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """

    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        other = form[self.fieldname]
        if field.data == other.data:
            raise ValidationError("Target language cannot be source language!")
        

class CustomSelectMultipleField(SelectMultipleField):
    """
    Customized class I would like to use for multiple select windows. 
    TODO: configure customized class for multi select button
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    
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
    languages = SelectMultipleField("Select Your Languages")

class AddPostForm(FlaskForm):
    post = TextAreaField("New Post",validators=[Length(max=500), DataRequired()])
    submit = SubmitField("Submit")

class AddVocableForm(FlaskForm):
    nl = StringField('Dutch', validators=[Length(max=200)])
    de = StringField('German', validators=[Length(max=200)])
    en = StringField('English', validators=[Length(max=200)])
    fr = StringField('French', validators=[Length(max=200)])
    it = StringField('Italian', validators=[Length(max=200)])
    es = StringField('Spanish', validators=[Length(max=200)])
    submit = SubmitField("Submit")


    
class ConfigPracticeForm(FlaskForm):
    target_language = SelectField("Select Target Language", validators=[NotEqualTo("source_language")])
    source_language = SelectField("Select Source Language")
    submit = SubmitField()

class PracticeForm(FlaskForm):
    your_answer = StringField("Your Answer",validators=[Length(max=200)], widget=TextArea())
    submit = SubmitField()

class EmptyForm(FlaskForm):
    submit = SubmitField()

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class CookieConsentForm(FlaskForm):
    required = CheckboxInput("Required Cookies")
    analytics = CheckboxInput("Analytics Cookies")
    submit = SubmitField("Submit Cookie Selection")

