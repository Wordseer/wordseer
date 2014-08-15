from .base import Base
from app import db

class Count(db.Model, Base):
    """A base class for models that store counts.

    Because models like words and dependencies can overlap across different
    projects, we must store their counts separately so that they are
    properly scoped.
    """

    # Attributes

    type = db.Column(db.String(64))
    sentence_count = db.Column(db.Integer, index=True, default=0)
    document_count = db.Column(db.Integer, index=True, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    # Relationship

    project = db.relationship("Project")

    # Inheritence

    __mapper_args__ = {
        "polymorphic_identity": "count",
        "polymorphic_on": type
    }

class WordCount(Count):
    """Model to store counts for words.
    """

    # We need to redefine ID here for polymorphic inheritance
    id = db.Column(db.Integer, db.ForeignKey("count.id"), primary_key=True)

    # Belongs to a word
    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    word = db.relationship("Word")

    __mapper_args__ = {
        "polymorphic_identity": "word_count",
    }

class SequenceCount(Count):
    """Model to store counts for sequences.
    """

    # We need to redefine ID here for polymorphic inheritance
    id = db.Column(db.Integer, db.ForeignKey("count.id"), primary_key=True)

    # Belongs to a sequence
    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"))
    sequence = db.relationship("Sequence")

    __mapper_args__ = {
        "polymorphic_identity": "sequence_count",
    }

class DependencyCount(Count):
    """Model to store counts for dependencies.
    """

    # We need to redefine ID here for polymorphic inheritance
    id = db.Column(db.Integer, db.ForeignKey("count.id"), primary_key=True)

    # Belongs to a dependency
    dependency_id = db.Column(db.Integer, db.ForeignKey("dependency.id"))
    dependency = db.relationship("Dependency")

    __mapper_args__ = {
        "polymorphic_identity": "dependency_count",
    }