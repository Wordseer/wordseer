"""Models for projects.
"""
from app import db
from .base import Base

class Project(db.Model, Base):
    """A WordSeer project for a collection of documents.

    Attributes:
        name (str): A human-readable name for this project.
        path (str): The location of the directory of the files of this project.
        user (User): The owner of this project.
        documents (list of Documents): ``Document``\s present in this project.
    """

    # Attributes
    name = db.Column(db.String)
    path = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Active project indicator
    active_project = None

    # Relationships
    document_files = db.relationship("DocumentFile",
        secondary="document_files_in_projects", backref="projects")
    structure_files = db.relationship("StructureFile", backref="project")
    logs = db.relationship("Log", backref="project")
    word_in_sentence = db.relationship("WordInSentence",
        backref="project", lazy="dynamic")
    sequence_in_sentence = db.relationship("SequenceInSentence",
        backref="project", lazy="dynamic")
    word_in_sequence = db.relationship("WordInSequence",
        backref="project", lazy="dynamic")
    dependency_in_sentence = db.relationship("DependencyInSentence",
        backref="project", lazy="dynamic")

    def get_documents(self):
        """A method to get all the ``Document``\s that are in this project.

        Returns:
            list of ``Document``\s.
        """

        documents = []

        for document_file in self.document_files:
            documents.extend(document_file.documents)

        return documents

    def frequent_sequences(self, position, length, limit, lemmatized = False):
        """Return the most frequently occurring sequences with the given
        parameters.
        """

        seq_sents = self.sequence_in_sentence.\
            filter_by(position=position).\
            join("sequence").\
            filter_by(length=length).\
            filter_by(lemmatized=lemmatized).\
            group_by("sequence_id").\
            order_by("sentence_count DESC").\
            limit(limit)

        return [seq_sent.sequence for seq_sent in seq_sents]

    def frequent_words(self, part_of_speech, position, limit):
        """Return the most frequently occurring words with the given parameters
        """

        word_sents = self.word_in_sentence.\
            filter_by(position=position).\
            join("word").\
            filter("Word.part_of_speech like '{0}%'".format(part_of_speech)).\
            group_by("word_id").\
            limit(limit)

        return [word_sent.word for word_sent in word_sents]