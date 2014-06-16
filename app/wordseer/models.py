"""These are the models for the wordseer website.
"""

from sqlalchemy.ext.declarative import declared_attr

from app import db
from app.models import Base
from app.models import User

# Association tables
sentences_in_sentencesets = db.Table("sentences_in_sentencesets",
    db.metadata,
    db.Column("sentence_id", db.Integer, db.ForeignKey("sentence.id")),
    db.Column("sentenceset_id", db.Integer, db.ForeignKey("sentence_set.id"))
)

#TODO: are we going to have a Document object?
documents_in_documentsets = db.Table("documents_in_documentsets",
    db.metadata,
    db.Column("document_id", db.Integer, db.ForeignKey("unit.id")),
    db.Column("documentset_id", db.Integer, db.ForeignKey("document_set.id"))
)

sentences_in_queries = db.Table("sentences_in_queries",
    db.metadata,
    db.Column("sentence_id", db.Integer, db.ForeignKey("sentence.id")),
    db.Column("query_id", db.Integer, db.ForeignKey("cachedsentences.id"))
)

sequences_in_sequencesets = db.Table("sequences_in_sequencesets",
    db.metadata,
    db.Column("sequence_id", db.Integer, db.ForeignKey("sequence.id")),
    db.Column("sequenceset_id", db.Integer, db.ForeignKey("sequence_set.id")),
)

class Set(db.Model, Base):
    """This is the basic ``Set`` class.

    ``Set``s are made of either ``Sequence``s, ``Sentence``s and ``Document``s.
    A ``Set`` model has an association with a ``User`` and has some properties
    like a name and a creation date.

    The more specialized type of ``Set``s (like ``SequenceSet``s, etc) inherit
    from this table.

    Attributes:
        user (User): The ``User`` that owns this ``Set``
        name (str): The name of this ``Set``
        creation_date (str): A ``date.DateTime`` object of when this ``Set`` was
            created.
        type (str): The type of ``Set`` that this is.
    """

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String)
    creation_date = db.Column(db.Date)
    type = db.Column(db.String)

    __mapper_args__ = {
        "polymorphic_identity": "set",
        "polymorphic_on": type,
    }

class SequenceSet(Set, db.Model):
    """A ``Set`` that can have a list of ``Sequences`` in it.

    The ``type`` attribute a ``SequenceSet`` is set to ``sequenceset``.

    Attributes:
        sequences (list): A list of ``Sequence``s in this ``SequenceSet``.
    """

    #__tablename__ = "sequenceset"

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    sequences = db.relationship("Sequence",
        secondary=sequences_in_sequencesets,
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "sequenceset",
    }

class SentenceSet(Set, db.Model):
    """A ``Set`` that can have a list of ``Sentences`` in it.

    The ``type`` attribute of a ``SentenceSet`` is set to ``sentenceset``.

    Attributes:
        sentences (list): A list of ``Sentence``s in this ``SentenceSet``.
    """

    #__tablename__ = "sentenceset"

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    sentences = db.relationship("Sentence",
        secondary=sentences_in_sentencesets,
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "sequenceset",
    }

class DocumentSet(Set, db.Model):
    """A Set that can have a list of ``Document``s in it.

    The ``type`` attribute of a ``DocumentSet`` is set to ``sentenceset``.

    Attributes:
        documents (list): A list of ``Document``s in this ``DocumentSet``.
    """

    #__tablename__ = "documentset"

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    documents = db.relationship("Unit",
        secondary=documents_in_documentsets,
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "sequenceset",
    }

class CachedSentences(db.Model, Base):
    """Cached list of ``Sentences`` for a query.

    When a ``User`` does a query we pre-compute the set of sentences that
    matches this query so that the 5 default views (of the JavaScript frontend)
    don't all have to compute it separately.

    This model stores the relevant query ID and a list of Sentences.
    The query ID of a given entry is its ID.

    Attributes:
        sentences (list): A list of ``Sentence``s connected with this query.
    """

    sentences = db.relationship("Sentence",
        secondary=sentences_in_queries)

class PropertyMetadata(db.Model, Base):
    """Describes ``Property`` objects of the same type: metametadata, if you
    will.

    ``Property``s must have additional data attached to it to describe to
    wordseer what should be done with it.

    Attributes:
        type (str): The type of these ``Property``s (string, int, date, etc.)
        filterable (boolean): If True, then this ``Property`` object should be
            filterable in the wordseer interface.
        display_name (str): The name of the property that this object is
            describing; this is the same as the ``name`` of the
            ``Property`` object described.
        display (boolean): If True, then the ``Property`` objects described
            by this object should have their names and values described in
            the reading view on the frontend.
    """

    type = db.Column(db.String)
    is_category = db.Column(db.Boolean)
    display_name = db.Column(db.String)
    display = db.Column(db.Boolean)

