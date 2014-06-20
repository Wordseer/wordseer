from app import db
from base import Base

class WordInSentence(db.Model, Base):
    """Association object for words in sentences
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    position = db.Column(db.Integer)
    space_before = db.Column(db.String)
    tag = db.Column(db.String)

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
    """Association object for sequences in sentences
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
    """Association object for words in sequences
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
