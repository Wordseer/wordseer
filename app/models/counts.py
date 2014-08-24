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
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), index=True)

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

    @classmethod
    def fast_find_or_initialize(cls, query, **kwargs):
        """Use a query to see if a row exists.
        """
        tablename = cls.__tablename__
        query_base = ("FROM count JOIN %s ON count.id = word_count.id "
            "WHERE %s LIMIT 1") % (tablename, query)
        #query = "SELECT * %s LIMIT 1" % query_base
        query = "SELECT EXISTS (SELECT 1 %s)" % query_base
        match = db.session.execute(query).fetchone()
        if match == (1,):
            return db.session.execute(("SELECT"
                " sentence_count %s") % query_base).fetchone()
        else:
            new_record = cls(**kwargs)
            new_record.save(force=False)
            return new_record

class SequenceCount(Count):
    """Model to store counts for sequences.
    """

    # We need to redefine ID here for polymorphic inheritance
    id = db.Column(db.Integer, db.ForeignKey("count.id"), primary_key=True)

    # Belongs to a sequence
    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"), index=True)
    sequence = db.relationship("Sequence")

    __mapper_args__ = {
        "polymorphic_identity": "sequence_count",
    }

    @classmethod
    def fast_find_or_initialize(cls, query, **kwargs):
        """Use a query to see if a row exists.
        """
        tablename = cls.__tablename__
        query_base = ("FROM count JOIN %s ON count.id = sequence_count.id "
            "WHERE %s LIMIT 1") % (tablename, query)
        #query = "SELECT * %s LIMIT 1" % query_base
        query = "SELECT EXISTS (SELECT 1 %s)" % query_base
        match = db.session.execute(query).fetchone()
        if match == (1,):
            return db.session.execute(("SELECT document_count, "
                " sentence_count %s") % query_base).fetchone()
        else:
            new_record = cls(**kwargs)
            new_record.save(force=False)
            return new_record

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

    @classmethod
    def fast_find_or_initialize(cls, query, **kwargs):
        """Use a query to see if a row exists.
        """
        tablename = cls.__tablename__
        query_base = ("FROM count JOIN %s ON count.id = dependency_count.id "
            "WHERE %s LIMIT 1") % (tablename, query)
        #query = "SELECT * %s LIMIT 1" % query_base
        query = "SELECT EXISTS (SELECT 1 %s)" % query_base
        match = db.session.execute(query).fetchone()
        if match == (1,):
            return db.session.execute(("SELECT document_count, "
                " sentence_count %s") % query_base).fetchone()
        else:
            new_record = cls(**kwargs)
            new_record.save(force=False)
            return new_record

