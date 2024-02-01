from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional 
import sqlalchemy as sa 
import sqlalchemy.orm as so
from flask_login import UserMixin
from app import db, login
from hashlib import md5

@login.user_loader 
def load_user(id): 
    return db.session.get(User, int(id))


class UserVocable(db.Model):
    __tablename__ = "user_vocable"

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), primary_key=True)
    vocable_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('vocable.id'), primary_key=True)
    nl_level: so.Mapped[int] = so.mapped_column( nullable=True, default=0)
    en_level:  so.Mapped[int] = so.mapped_column( nullable=True, default=0)
    fr_level:  so.Mapped[int] = so.mapped_column( nullable=True, default=0)
    de_level:  so.Mapped[int] = so.mapped_column( nullable=True, default=0)
    it_level:  so.Mapped[int] = so.mapped_column( nullable=True, default=0)
    es_level:  so.Mapped[int] = so.mapped_column( nullable=True, default=0)


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    vocables: so.WriteOnlyMapped['Vocable'] = so.relationship(
        secondary=UserVocable,
        
    )
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"
    

class Post(db.Model):
    __tablename__="post"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    author: so.Mapped[User] = so.relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post {self.body}>"
    

class Vocable(db.Model):
    __tablename__ = "vocable"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    nl: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    en: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    fr: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    de: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    it: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    es: so.Mapped[str] = so.mapped_column(sa.String(length=100), nullable=True)
    is_common: so.Mapped[bool] = so.mapped_column(default=False)
    
    def __repr__(self) -> str:
        return f"English: {self.en}, Commonly used: {self.is_common}"
    

