from flask.ext.security import RoleMixin
from flask.ext.security import UserMixin

from app import db

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
    roles = db.relationship('Role', secondary="roles_users",
        backref=db.backref('users', lazy='dynamic'))

    sets = db.relationship("Set", backref="user")
    projects = db.relationship("Project", backref="user")

    def has_document(self, document):
        """Check if this user owns this document.
        """

        return any([project in self.projects for project in document.projects])
