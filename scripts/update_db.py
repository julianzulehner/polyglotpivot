from app import app
from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import Language 

languages = []
for iso, name in app.config['LANGUAGES'].items():
    if not db.session.scalar(sa.select(Language).where(Language.iso == iso)):
        languages.append(Language(iso=iso,name=name))
db.session.add_all(languages)
db.session.commit()
print('Languages created')

