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
        part_of_speech (str): The part of speech of ``word``.
        surface (str): The ``Word`` with exact capitalization.
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    position = db.Column(db.Integer)
    space_before = db.Column(db.String)
    part_of_speech = db.Column(db.String)
    surface = db.Column(db.String)

    project = db.relationship("Project")

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "word_in_sentence", cascade="all, delete-orphan"))

    word = db.relationship("Word",
        backref=db.backref(
            "word_in_sentence", cascade="all, delete-orphan"))

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
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    position = db.Column(db.Integer)

    project = db.relationship("Project")
    document = db.relationship("Document")

    sequence = db.relationship("Sequence",
        backref=db.backref(
            "sequence_in_sentence", cascade="all, delete-orphan"))

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "sequence_in_sentence", cascade="all, delete-orphan"))

class WordInSequence(db.Model, Base):
    """Association object for words in sequences.

    Attributes:
        word (Word): The ``Word`` in this relationship.
        sequence (Sequence): The ``Sequence`` in this relationship.
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    project = db.relationship("Project")

    word = db.relationship("Word",
        backref=db.backref(
            "word_in_sequence", cascade="all, delete-orphan"))

    sequence = db.relationship("Sequence",
        backref=db.backref(
            "word_in_sequence", cascade="all, delete-orphan"))

class DependencyInSentence(db.Model, Base):
    """Association object for dependencies in sentences.

    Attributes:
        dependency (Dependency): The ``Dependency`` in this relationship.
        sentence (Sentence): The ``Sentence`` in this relationship.
        governor_index (int): The position (0-indexed) of the governor of
            ``dependency`` in ``sentence``.
        dependent_index (int): The position (0-indexed) of the dependent of
            ``dependency`` in ``sentence``.
        governor_part_of_speech (str): The part of speech of the governor.
        dependent_part_of_speech (str): The part of speech of the dependency.
    """
    #TODO: is POS redundant here?

    dependency_id = db.Column(db.Integer, db.ForeignKey("dependency.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    governor_index = db.Column(db.Integer)
    dependent_index = db.Column(db.Integer)
    governor_part_of_speech = db.Column(db.String)
    dependent_part_of_speech = db.Column(db.String)

    project = db.relationship("Project")
    document = db.relationship("Document")

    dependency = db.relationship("Dependency",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"))

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"))

