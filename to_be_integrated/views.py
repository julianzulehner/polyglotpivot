from flask import redirect, url_for, flash, render_template
from src import accounts_bp
from src.accounts.forms import LoginForm, RegisterForm

@accounts_bp.route('/login',methods=['POST','GET'])
def login(): 
    form = LoginForm()        
    return render_template('accounts/login.html', form=form)


@accounts_bp.route('/register',methods=['POST','GET'])
def register():
    form = RegisterForm()
    return render_template('accounts/register.html', form=form)

@accounts_bp.route('/settings')
def settings():
    return render_template('accounts/settings.html')