from flask import Flask, request
from config import Config 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler 
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
mail = Mail(app)
login.login_view = 'login'

@app.context_processor
def inject_template_scope():
    injections = dict()   
    def cookies_check():
        required_cookies = request.cookies.get('required_cookies_consent')
        analytics_cookies = request.cookies.get('analytics_cookies_consent')
        return required_cookies == 'true'
    injections.update(cookies_check=cookies_check)
    return injections

if not app.debug:

    # SEND EMAIL IN CASE OF ERROR
    if app.config['MAIL_SERVER']:
        auth = None 
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure=None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                       fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                                       toaddrs=app.config['ADMINS'], 
                                       subject='Polyglotpivot Failure',
                                       credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    # LOG TO FILE IN CASE OF ERROR
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/polyglotpivot.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Polyglotpivot startup')

    

from app import routes, models, errors 
