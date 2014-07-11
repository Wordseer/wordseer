"""The Document model.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from .base import Base
from .unit import Unit

class Document(Unit):
    """A model for a single document file.

    Documents are top-level Units. See the description in the Unit model for
    further details.

    Attributes:
        title (str): the title of the document
        path (str): the location of the file on the system

    Relationships:
        has one: unit
        has many: sentences
        belongs to: collection
    """

    # Attributes
    # We need to redefine ID here for polymorphic inheritance
    id = db.Column(db.Integer, db.ForeignKey("unit.id"), primary_key=True)
    title = db.Column(db.String, index=True)
    path = db.Column(db.String)
    sentence_count = db.Column(db.Integer)

    # Relationships
    parent_id = None
    parent = None
    #children = db.relationship("Unit", backref="parent") FIXME: No parents

    __mapper_args__ = {
        "polymorphic_identity": "document",
    }

    def belongs_to(self, user):
        """Check if this ``Document`` belongs to this ``User``.

        Arguments:
            user (User): A ``User`` to check ownership to.

        Returns:
            ``True`` if this ``Document`` is in any of the ``Project``s owned
            by ``user``, ``False`` otherwise.
        """

        return any([project in user.projects for project in self.projects])

    def __repr__(self):
        return "<Document: " + str(self.title) + ">"

    @property
    def sentences(self):
        """Temp proxy method
        """

        return self.all_sentences
