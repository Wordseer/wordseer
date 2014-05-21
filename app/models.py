"""
Models for the wordseer frontend as a whole.

These models set up user authentication, which is used by all blueprints in
the application.
"""

from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from sqlalchemy.ext.declarative import declared_attr

from app import db

class Base(object):
    """This is a mixin to add to Flask-SQLAlchemy's db.Model class.
    """

    # Define the primary key
    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def save(self):
        """Commits this model instance to the database

        TODO: should return either True or False depending on its success.
        TODO: manage sequential saves better.

        """
        db.session.add(self)
        db.session.commit()

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    """Represents a flask-security user role.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    """Represents a flask-security user.
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'))
