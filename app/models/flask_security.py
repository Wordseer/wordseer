"""Models needed for flask-security.
"""
from flask.ext.security import RoleMixin
from flask.ext.security import UserMixin

from app import db
from .base import Base

class Role(db.Model, Base, RoleMixin):
    """Represents a flask-security user role.

    Attributes:
        name (str): Name of this role.
        description (str): Description of this role.
        users (list of Users): ``User``\s who have this role.
    """
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, Base, UserMixin):
    """Represents a flask-security user.

    Attributes:
        email (str): The user's email.
        password (str): The user's email.
        active (boolean): If the user is active.
        confirmed_at (datetime): When the user confirmed their account.
        roles (list of Roles): ``Role``\s that this ``User`` has.
        sets (list of Sets): ``Set``\s that this ``User`` has.
        projects (list of Projects): ``Project``\s that this ``User`` has.
    """

    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary="roles_users",
        backref=db.backref('users', lazy='dynamic'))

    sets = db.relationship("Set", backref="user")
    projects = db.relationship("Project", backref="user")

    def has_document_file(self, document_file):
        """Check if this user owns this `DocumentFile`.

        Arguments:
            document_file (DocumentFile): A ``DocumentFile`` to check ownership
                of.

        Returns:
            ``True`` if the given ``DocumentFile`` is present in at least one of
            the projects that this user owns. ``False`` otherwise.
        """

        return any([project in self.projects for project in
            document_file.projects])

    def has_document(self, document):
        """Check if this user owns this ``Document``.

        Arguments:
            document (Document): A ``Document`` to check ownership of.

        Returns:
            ``True`` if the given ``Document`` is present in at least one of the
            projects that this user owns. ``False`` otherwise.
        """

        return any([project in self.projects for project in
            document.document_file.projects])

