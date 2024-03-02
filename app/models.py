"""
This module contains all sqlalchemy ORM classes to handle database objects of the 
polyglotpivot project. 
"""

from __future__ import annotations

from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional 
import sqlalchemy as sa 
import sqlalchemy.orm as so
from flask_login import UserMixin
from app import db, login, app
from hashlib import md5
from sqlalchemy.sql.expression import func 
from time import time
import jwt

@login.user_loader 
def load_user(id: int|str) -> User|None:
    """
    Returns the current_user object. 
    This function is needed when using flask-login extension.
    """
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
    
    def set_password(self:User, password:str) -> None:
        """
        Sets the password hash to the User instance.
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self:User, password:str) -> bool: 
        '''
        Checks if User password is right and returns True or False.
        This is used during the login procedure.
        '''
        return check_password_hash(self.password_hash, password)
    
    
    def set_languages(self: User, languages:list[str]) -> None:
        '''
        Sets the languages a User has. The argument languages is a list of
        languages as string e.g ['English','German']. It is important that
        that there is an entry in the Vocable table with the corresponding
        Vocable.name
        '''
        query = sa.select(Language).where(Language.name.in_(languages))
        new_languages = db.session.scalars(query).all()
        self.languages = new_languages
        db.session.commit()

    def get_random_vocable(self: User, source_language:Language, target_language:Language, level:int|None=None):
            '''
            Returns a random instance of class Vocable of a User. By setting the level argument one can 
            filter for the level. The level can be from 0 (new) to 6 (learned). It only returns vocable
            that are both defined in target and source language.
            '''
            if level:
                query = sa.select(Vocable.id).where(sa.and_(Vocable.user_id == self.id,
                            getattr(Vocable, target_language.iso) != "",
                            getattr(Vocable, source_language.iso) != "",
                            getattr(Vocable, f"{target_language.iso}_lvl") == level)).order_by(func.random())
            else: 
                query = sa.select(Vocable.id).where(sa.and_(Vocable.user_id == self.id,
                            getattr(Vocable,target_language.iso) != "",
                            getattr(Vocable,source_language.iso) != "")).order_by(func.random())
            return db.session.scalar(query)

    def get_due_vocable(self, source_language:Language, target_language:Language, level:int|None=None) -> Vocable:
        '''
        Returns the vocable that was not practiced for the longest time according
        to the database entry of the Practice table.
        '''
        #TODO: implement 
        pass
            
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password':self.id, 'exp':time()+ expires_in},
                          app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)

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
    pt: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    
    nl_lvl: so.Mapped[int] = so.mapped_column(default=0)
    en_lvl: so.Mapped[int] = so.mapped_column(default=0)
    fr_lvl: so.Mapped[int] = so.mapped_column(default=0)
    de_lvl: so.Mapped[int] = so.mapped_column(default=0)
    it_lvl: so.Mapped[int] = so.mapped_column(default=0)
    es_lvl: so.Mapped[int] = so.mapped_column(default=0)
    pt_lvl: so.Mapped[int] = so.mapped_column(default=0)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    
    practices: so.Mapped[list['Practice']]=so.relationship(back_populates='vocable')
    user: so.Mapped['User']=so.relationship(back_populates='vocables')


    
    def __repr__(self):
        return f"<Vocable {self.id}, English: {self.en}>"
    
    def rise_level(self, language:Language):
        current_level = self.__getattribute__(language.iso + "_lvl")
        if current_level < 6:
            self.__setattr__(language.iso + "_lvl", current_level+1)
            db.session.commit()

    def check_result(self, answer:str, targetlanguage:Language):
        if answer == getattr(self, targetlanguage.iso): 
            self.rise_level(targetlanguage)
            self.add_practice(True)
            return True
        return False 

    def add_practice(self, isanswercorrect:bool) -> None:
        '''
        Adds a practice entry to the practice table.
        '''
        practice = Practice(iscorrect=isanswercorrect,vocable_id=self.id)
        self.practices.append(practice)
        db.session.commit()
    
    def check_if_studied(self:Vocable) -> bool:
        '''
        Checks if a Vocable was already studied before. And returns
        True or False.
        '''
        return True if self.practices else False
        
    
class Post(db.Model):
    '''
    The class post defines the post table. A post is a message a user (class:User) can 
    create. 
    '''
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
    source_language_id: so.Mapped[str] = so.mapped_column(sa.String(length=50),nullable=True)
    target_language_id: so.Mapped[str] = so.mapped_column(sa.String(length=50),nullable=True)    
    vocable_id: so.Mapped[int] = so.mapped_column(nullable=True)
    vocable_level: so.Mapped[int] = so.mapped_column(nullable=True)

    user: so.Mapped[User] = so.relationship(back_populates="session")

    def clear(self):
        self.source_language_id = None
        self.target_language_id = None
        self.vocable_id = None
        self.vocable_level = None 
        db.session.commit()

class Practice(db.Model):
    __tablename__ = 'practice'

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    iscorrect: so.Mapped[bool] = so.mapped_column(sa.Boolean, nullable=False)
    vocable_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Vocable.id))

    vocable: so.Mapped['Vocable']=so.relationship(back_populates='practices')





    

