from flask import Flask, render_template, request, url_for, flash, redirect
from forms import SignUpForm, LoginForm
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session
from database_orm import Vocable, User, Language, UserLanguage, UserVocable, VocableCategory
from functions import get_db_connection, get_post, get_all_posts
import pandas as pd
from flask_login import LoginManager



app = Flask(__name__)
app.config['SECRET_KEY'] = 'study4fun'

login_manager = LoginManager()
login_manager.init_app(app)

engine = create_engine(url="sqlite:///database.db",echo=True)
session = Session(bind=engine)

users_data = session.query(User).all()
vocabulary_data = session.query(Vocable).all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=('GET', 'POST'))
def create(): 
    if request.method == 'POST':
        en = request.form['english']
        de = request.form['german']
        nl = request.form['dutch']
        es = request.form['spanish']

        new_vocable = Vocable(en=en,de=de,nl=nl, es=es)
        new_vocable.users = []
        session.add(new_vocable)
        session.commit()
        flash("New vocable was added.","success")
        return redirect(url_for('vocabulary'))
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    vocable = session.execute(select(Vocable).filter_by(id=id)).scalar_one()

    if request.method == 'POST':
        vocable.en = request.form['english']
        vocable.de = request.form['german']
        vocable.nl = request.form['dutch']
        vocable.es = request.form['spanish']

        session.commit()
        
        return redirect(url_for('vocabulary'))

    return render_template('edit.html', post=vocable)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    row_to_delete = session.query(Vocable).where(Vocable.id == id)
    row_to_delete.delete()
    session.commit()
    flash('Vocable was successfully deleted!','success')
    return redirect(url_for('vocabulary'))
    
@app.route('/contact')
def about():
    return render_template('contact.html')
    
@app.route('/vocabulary')
def vocabulary():
    with Session(engine) as session: 
        query = session.query(Vocable)
        posts = pd.read_sql(query.statement, query.session.bind)
    return render_template('vocabulary.html', posts=posts)

@app.route('/practice')
def practice():
    posts = get_all_posts()
    return render_template('practice.html', posts=posts)

# -- LOGIN: Login with existing account --
@app.route('/login',methods=['POST','GET'])
def login(): 
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        df = pd.read_sql_query(f"SELECT * FROM users WHERE(email='{form.email.data}')",conn)
        if df.shape[0] == 0: # user not registered
             flash("Login failed. Email or password wrong!", "danger")
             return redirect(url_for('login'))
        if df.shape[0] == 1: # user exists
            if (form.email.data == df.email[0]) & (form.password.data == df.password[0]):
                flash(f"Welcome back {df.username[0]}!",'success')
                return redirect(url_for('index'))
            else: 
                flash("Login failed. Email or password wrong!", "danger")
                return redirect(url_for('login'))
        
    return render_template('login.html', form=form)

# -- REGISTER: Create an account --
@app.route('/register',methods=['POST','GET'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        # Check if user already existsemail_exists = conn.execute("SELECT COUNT(1) FROM users WHERE email = '{form.email.data}'").fetchone()[0]
        email_exists = conn.execute(f"SELECT COUNT(1) FROM users WHERE email = '{form.email.data}'").fetchone()[0]
        username_exists = conn.execute(f"SELECT COUNT(1) FROM users WHERE username = '{form.username.data}'").fetchone()[0]
        if (email_exists == 0) & (username_exists == 0): # user available
            conn.execute(f"INSERT INTO users (username, email, password) VALUES ('{form.username.data}', '{form.email.data}', '{form.password.data}')")
            flash(f"Account created for {form.username.data}!", "success")
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        elif username_exists == 1:
            flash("This username is already in use.",'danger')
            conn.close()
            return redirect(url_for('register'))
        else:
            flash("This email is already in use.",'danger')
            conn.close()
            return redirect(url_for('register'))
    return render_template('register.html', form=form)

@app.route('/settings')
def settings():
    return render_template('settings.html')