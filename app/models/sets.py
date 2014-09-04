"""Set models.
"""

from app import db
from .base import Base

class Set(db.Model, Base):
    """This is the basic ``Set`` class.

    ``Set``\s contain other objects; by default, there are ``DocumentSet``\s,
    ``SentenceSet``\s, and ``BigramSet``\s, containing ``Document``\s,
    ``Sentence``\s, and ``Bigram``\s respectively.

    A ``Set`` model has an association with a ``User`` and has some properties
    like a name and a creation date.

    The more specialized type of ``Set``\s (like ``BigramSet``\s, etc) inherit
    from this class.

    Attributes:
        user (User): The ``User`` that owns this ``Set``
        name (str): The name of this ``Set``
        creation_date (str): A ``date.DateTime`` object of when this ``Set`` was
            created.
        type (str): The type of ``Set`` that this is.
    """

    # Attributes
    # We need to redefine ID to nest sets
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String)
    creation_date = db.Column(db.Date)
    type = db.Column(db.String)
    parent_id = db.Column(db.Integer, db.ForeignKey("set.id"))

    # Relationships
    children = db.relationship("Set", backref=db.backref("parent",
        remote_side=[id]))

    __mapper_args__ = {
        "polymorphic_identity": "set",
        "polymorphic_on": type,
    }

    def get_items(self):
        """Subclasses of ``Set`` should override this method to return a list
        of whatever they are ``Set``\s of.
        """

        raise NotImplementedError()

class BigramSet(Set):
    """A ``Set`` that can have a list of ``Bigrams`` in it.

    The ``type`` attribute a ``BigramSet`` is set to ``bigramset``.

    Attributes:
        bigrams (list): A list of ``Bigram``\s in this ``BigramSet``.
    """

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    bigrams = db.relationship("Bigram",
        secondary="bigrams_in_bigramsets",
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "bigramset",
    }

    def get_items(self):
        """Return the ``Bigram``\s associated with this ``BigramSet``.

        Returns:
            list of Bigrams
        """

        return self.bigrams

class SentenceSet(Set):
    """A ``Set`` that can have a list of ``Sentences`` in it.

    The ``type`` attribute of a ``SentenceSet`` is set to ``sentenceset``.

    Attributes:
        sentences (list): A list of ``Sentence``\s in this ``SentenceSet``.
    """

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    sentences = db.relationship("Sentence",
        secondary="sentences_in_sentencesets",
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "sentenceset",
    }

    def get_items(self):
        """Return the ``Sentence``\s associated with this ``SentenceSet``.

        Returns:
            list of Sentences
        """

        return self.sentences

class DocumentSet(Set):
    """A Set that can have a list of ``Document``\s in it.

    The ``type`` attribute of a ``DocumentSet`` is set to ``sentenceset``.

    Attributes:
        documents (list): A list of ``Document``\s in this ``DocumentSet``.
    """

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    documents = db.relationship("Document",
        secondary="documents_in_documentsets",
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "documentset",
    }

    def get_items(self):
        """Return the ``Document``s associated with this ``DocumentSet``.

        Returns:
            list of Documents
        """

        return self.documents

