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

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"), index=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    position = db.Column(db.Integer)
    space_before = db.Column(db.String)
    part_of_speech = db.Column(db.String)
    surface = db.Column(db.String)

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
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), index=True)
    position = db.Column(db.Integer)

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

    dependency = db.relationship("Dependency",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"))

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"))

class ProjectsUsers(db.Model, Base):
    """Associate Users with Projects.

    Attributes:
        user (User): The ``User`` in this relationship.
        project (Project): The ``Project`` in this relationship.
        role (int): The permissions of this ``User`` in this ``Project``.
        ROLE_USER (int): The integer that represents a user role for
            ``permissions``.
        ROLE_ADMIN (int): Represents an admin role for ``permissions``.
    """
    ROLE_USER = 0
    ROLE_ADMIN = 1

    ROLE_DESCRIPTIONS = {
        ROLE_USER: "User",
        ROLE_ADMIN: "Admin"
    }

    def get_role_name(self):
        """Return a human-readable role name.
        """
        return self.ROLE_DESCRIPTIONS[self.role]

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    project_id = db.Column(db.Integer(), db.ForeignKey("project.id"))
    role = db.Column(db.Integer())

    user = db.relationship("User", backref=db.backref("user_projects",
        cascade="all, delete-orphan"))

    project = db.relationship("Project", backref=db.backref("project_users",
        cascade="all, delete-orphan"))

class BigramOffset(db.Model, Base):
    """This represents a bigram with a certain offset.
    """

    offset = db.Column(db.Integer(), nullable=False)
    frequency = db.Column(db.Integer(), default=0)
    bigram_id = db.Column(db.Integer, db.ForeignKey("bigram.id"))
    sentences = db.relationship("Sentence", secondary="bigrams_in_sentences",
        backref="bigrams")

    def add_sentence(self, sentence, force=True):
        """Add a sentence to the ``sentences`` attribute and update frequency
        accordingly.

        Arguments:
            sentence (Sentence): A Sentence to add to this BigramOffset.
            force (bool): If ``True``, save and commit to the database.
        """
        self.sentences.append(sentence)
        self.frequency += 1

        self.save(force)

