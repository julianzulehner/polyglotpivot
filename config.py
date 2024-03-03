import os
basedir = os.path.abspath(os.path.dirname(__file__))

# This is the config of my main branch.

class Config: 
    SECRET_KEY = os.environ.get("SECRET_KEY") or '5ce75b535d368562838b7f6cac05b344'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://polyglotpivot:@localhost:3306/polyglotpivot'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['polyglotpivot@gmail.com']
    POSTS_PER_PAGE = 5
    VOCABLES_PER_PAGE = 25
    CONSENT_FULL_TEMPLATE= 'consent.html'
    CONSENT_BANNER_TEMPLATE = 'consent_banner.html'
    LANGUAGES = {'de':'German',
                 'en':'English',
                 'es':'Spanish', 
                 'fr':'French',
                 'it':'Italian',
                 'nl':'Dutch',
                 'pt':'Portuguese'}

