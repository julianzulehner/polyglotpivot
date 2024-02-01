import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):
    __tablename__ = 'user'

    # Data fields
    id: so.Mapped[str] = so.mapped_column(primary_key=True)

    # Relationships
    vocables: so.WriteOnlyMapped[Vocable] =  db.relationship('Vocable', secondary='uservocable', back_populates='users')

class Vocable(db.Model):
    __tablename__ = 'vocable'
    id = db.Column(db.Integer, primary_key=True)

class UserVocable(db.Model):
    __tablename__ = 'uservocable'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    vocable_id = db.Column(db.Integer, db.ForeignKey('vocable.id'), primary_key=True)