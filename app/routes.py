from app import app
from flask import redirect, render_template, url_for, flash, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, AddPostForm
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
import sqlalchemy as sa 
from app import db 
from app.models import User, Post, Language
from datetime import datetime, timezone

@app.route('/')
@app.route('/index', methods=["GET","POST"])
@login_required
def index():
    form = AddPostForm()
    if form.validate_on_submit():
        new_post = Post(body=form.post.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash("Post was added, successfully!", 'success')
        form.post.data = ""
        return redirect(url_for("index"))
    elif request.method == "GET":
        form.post.data = ""
    else:
        print(f"validate_on_submit: {form.validate_on_submit()}")
    posts = db.session.scalars(sa.select(Post).order_by(Post.timestamp.desc())).all()
    return render_template("index.html", title="Home", posts=posts, form=form)

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        query = sa.select(User).where(User.username == form.username.data)
        user = db.session.scalar(query)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("login.html",title="Sign In",form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=["GET","POST"])
def register():
    if current_user.is_authenticated: 
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Contratulations, you are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/user/<username>")
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = db.session.scalars(user.posts.select()).all()
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route("/edit_profile",methods=["GET","POST"])
@login_required
def edit_profile(): 
    form = EditProfileForm()
    languages = db.session.scalars(sa.select(Language.name)).all()
    form.languages.choices = languages
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.", 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html",title="Edit Profile", form=form)