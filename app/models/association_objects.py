"""Association objects for many-to-many relationships that require further
detail than simply two foreign key columns.
"""

from app import db
from base import Base

class WordInSentence(db.Model, Base):
    """Association object for ``Word``\s in ``Sentence``\s.

    Attributes:
        word (Word): The ``Word`` in this relationship.
        sentence (Sentence): The ``Sentence`` in this relationship.
        position (int): The position of ``word`` in ``sentence``.
        space_before (str): The space before ``word`` (if any).
        tag (str): The part of speech of ``word``.
        surface (str): The ``Word`` with exact capitalization.
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    position = db.Column(db.Integer)
    space_before = db.Column(db.String)
    tag = db.Column(db.String)
    surface = db.Column(db.String)

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "word_in_sentence", cascade="all, delete-orphan"
        )
    )

    word = db.relationship("Word",
        backref=db.backref(
            "word_in_sentence", cascade="all, delete-orphan"
        )
    )

    def __init__(self, word=None, sentence=None, position=None, space_before="",
        tag=""):

        self.word = word
        self.sentence = sentence
        self.position = position
        self.space_before = space_before
        self.tag = tag

class SequenceInSentence(db.Model, Base):
    """Association object for sequences in sentences.

    Attributes:
        sequence (Sequence): The ``Sequence`` in this relationship.
        sentence (Sentence): The ``Sentence`` in this relationship.
        position (int): The starting index (0-indexed) of ``sequence`` in
            ``sentence``.
    """

    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    position = db.Column(db.Integer)

    sequence = db.relationship("Sequence",
        backref=db.backref(
            "sequence_in_sentence", cascade="all, delete-orphan"
        )
    )

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "sequence_in_sentence", cascade="all, delete-orphan"
        )
    )

    def __init__(self, sequence=None, sentence=None, position=None):
        self.sequence = sequence
        self.sentence = sentence
        self.position = position

class WordInSequence(db.Model, Base):
    """Association object for words in sequences.

    Attributes:
        word (Word): The ``Word`` in this relationship.
        sequence (Sequence): The ``Sequence`` in this relationship.
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"))

    word = db.relationship("Word",
        backref=db.backref(
            "word_in_sequence", cascade="all, delete-orphan"
        )
    )

    sequence = db.relationship("Sequence",
        backref=db.backref(
            "word_in_sequence", cascade="all, delete-orphan"
        )
    )

class DependencyInSentence(db.Model, Base):
    """Association object for dependencies in sentences.

    Attributes:
        dependency (Dependency): The ``Dependency`` in this relationship.
        sentence (Sentence): The ``Sentence`` in this relationship.
        governor_index (int): The position (0-indexed) of the governor of
            ``dependency`` in ``sentence``.
        dependent_index (int): The position (0-indexed) of the dependent of
            ``dependency`` in ``sentence``.
    """

    dependency_id = db.Column(db.Integer, db.ForeignKey("dependency.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    governor_index = db.Column(db.Integer)
    dependent_index = db.Column(db.Integer)

    dependency = db.relationship("Dependency",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"
        )
    )

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"
        )
    )

    def __init__(self, dependency=None, sentence=None, governor_index=None,
        dependent_index=None):

        self.dependency = dependency
        self.sentence = sentence
        self.governor_index = governor_index
        self.dependent_index = dependent_index

