from flask import Flask, request
from config import Config 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager 
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler 
import os
from flask import current_app


db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mail.init_app(app)
    login.init_app(app)
    migrate.init_app(app)
    db.init_app(app)
    
    from app.errors import bp as errors_bp
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp, url_prefix="/main")
    


    if not app.debug and not app.testing:

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
   
    return app

from app import models

