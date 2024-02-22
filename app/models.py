from __future__ import annotations

from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional 
import sqlalchemy as sa 
import sqlalchemy.orm as so
from flask_login import UserMixin
from app import db, login
from hashlib import md5
import random
from sqlalchemy.sql.expression import func 

@login.user_loader 
def load_user(id): 
    return db.session.get(User, int(id))

user_language = sa.Table('user_language', 
                     db.metadata, 
                     sa.Column('user_id', sa.ForeignKey('user.id'), primary_key=True),
                     sa.Column('language_id', sa.ForeignKey('language.id'), primary_key=True))


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    languages: so.Mapped[list['Language']]= so.relationship(
        secondary=user_language, 
        back_populates='users')
    
    vocables: so.Mapped[list['Vocable']]=so.relationship(back_populates='user')
    posts: so.Mapped[list['Post']]=so.relationship(back_populates='author')
    session: so.Mapped['Session'] = so.relationship(back_populates='user')
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
    
    def set_languages(self, languages:list):
        query = sa.select(Language).where(Language.name.in_(languages))
        new_languages = db.session.scalars(query).all()
        self.languages = new_languages

    def get_random_vocable(self, language:Language, level=None):

        if level:
            return db.session.query(Vocable.id).filter(getattr(Vocable, language.iso + "_lvl") == level).order_by(func.random()).first()[0]
        else:
            return db.session.query(Vocable.id).order_by(func.random()).first()[0]

    

class Language(db.Model):
    __tablename__ = "language"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    iso: so.Mapped[str] = so.mapped_column(sa.String(length=2))
    name: so.Mapped[str] = so.mapped_column(sa.String(length=50))

    users: so.Mapped[list['User']] = so.relationship(
        secondary=user_language, 
        back_populates='languages')

    def __repr__(self):
        return f"<language {self.name}>"
    

class Vocable(db.Model):
    __tablename__ = "vocable"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    nl: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    en: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    fr: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    de: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    it: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    es: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    nl_lvl: so.Mapped[int] = so.mapped_column(default=0)
    en_lvl: so.Mapped[int] = so.mapped_column(default=0)
    fr_lvl: so.Mapped[int] = so.mapped_column(default=0)
    de_lvl: so.Mapped[int] = so.mapped_column(default=0)
    it_lvl: so.Mapped[int] = so.mapped_column(default=0)
    es_lvl: so.Mapped[int] = so.mapped_column(default=0)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))

    user: so.Mapped['User']=so.relationship(back_populates='vocables')

    
    def __repr__(self):
        return f"<Vocable {self.id}, English: {self.en}>"
    
    def rise_level(self, language:Language):
        current_level = self.__getattribute__(language.iso + "_lvl")
        if current_level < 6:
            self.__setattr__(language.iso + "_lvl", current_level+1)
            db.session.commit()

    def check_result(self, answer:str, targetlanguage:Language):
        if answer == self.__getattribute__(targetlanguage.iso): 
            self.rise_level(targetlanguage)
            return True
        return False 


    
        
    
class Post(db.Model):
    __tablename__="post"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(500))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f"<Post {self.body}>"
    

class Session(db.Model):
    __tablename__="session"

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), primary_key=True)
    source_language_id: so.Mapped[str] = so.mapped_column(nullable=True)
    target_language_id: so.Mapped[str] = so.mapped_column(nullable =True)    
    vocable_id: so.Mapped[str] = so.mapped_column(nullable=True)
    vocable_level: so.Mapped[int] = so.mapped_column(nullable=True)

    user: so.Mapped[User] = so.relationship(back_populates="session")

    def clear(self):
        self.source_language_id = None
        self.target_language_id = None
        self.vocable_id = None
        self.vocable_level = None 
        db.session.commit()

    

    

