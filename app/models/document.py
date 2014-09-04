"""The Document model.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from .base import Base
from .unit import Unit
from .mixins import NonPrimaryKeyEquivalenceMixin

class Document(Unit, NonPrimaryKeyEquivalenceMixin):
    """A model for a single document file.

    Documents are top-level Units. See the description in the Unit model for
    further details.

    Attributes:
        title (str): the title of the document
        projects (list of Projects): ``Project``\s that this ``Document`` is in.
        document_file (DocumentFile): The ``DocumentFile`` that this
            ``Document`` is a part of.

    Relationships:
        has one: unit
        has many: sentences
        belongs to: collection
    """

    # Attributes
    # We need to redefine ID here for polymorphic inheritance
    id = db.Column(db.Integer, db.ForeignKey("unit.id"), primary_key=True)
    title = db.Column(db.String, index=True)
    sentence_count = db.Column(db.Integer)
    document_file_id = db.Column(db.Integer, db.ForeignKey("document_file.id"))

    # Documents should not have parents
    parent_id = None
    parent = None

    # Relationships
    dependency_in_sentence = db.relationship("DependencyInSentence",
        backref="document", lazy="dynamic")

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
        return any([project in user.projects for project in
            self.document_file.projects])

    def __repr__(self):
        return "<Document: " + str(self.title) + ">"

