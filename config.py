import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config: 
    SECRET_KEY = os.environ.get("SECRET_KEY") or '5ce75b535d368562838b7f6cac05b344'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')