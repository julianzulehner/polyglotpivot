from app import app, db
from flask import redirect, render_template, url_for, flash, request
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, \
    ResetPasswordRequestForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa 
from app.models import User, Session, Language
from app.auth.email import send_password_reset_email
from app.auth import bp



@bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        query = sa.select(User).where(User.username == form.username.data)
        user = db.session.scalar(query)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        print(f"REMEMBER ME: {form.remember_me.data}")
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template("auth/login.html",title="Sign In",form=form)
    
@bp.route('/logout')
def logout():
    current_user.session.clear()
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=["GET","POST"])
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        session = Session()
        user.session = session
        db.session.add(user)
        db.session.commit()
        flash('Contratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template("auth/register.html", form=form)

@bp.route("/reset_password_request", methods=["GET","POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check you email for the instructions to reset your password','success')
        return redirect(url_for('auth/login'))
    return render_template('auth/reset_password_request.html',form=form)

@bp.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)

@bp.route("/edit_profile",methods=["GET","POST"])
@login_required
def edit_profile(): 
    form = EditProfileForm()
    languages = db.session.scalars(sa.select(Language.name)).all() # get all available languages
    form.languages.choices = languages # sets the available languages
    form.languages.data = [l.name for l in current_user.languages] # preselect the languages the user already has
    if form.validate_on_submit():
        form.languages.data = request.form.getlist('languages') # this updates the data according to the selection in the browser.
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.set_languages(form.languages.data)
        db.session.commit()
        flash("Your changes have been saved.", 'success')
        return redirect(url_for('auth.edit_profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("auth/edit_profile.html",title="Edit Profile", form=form)
