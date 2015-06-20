"""Models for projects.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from base import Base
from .log import Log
from .association_objects import ProjectsUsers

class Project(db.Model, Base):
    """A WordSeer project for a collection of documents.

    Attributes:
        name (str): A human-readable name for this project.
        path (str): The location of the directory of the files of this project.
        user (User): The owner of this project.
        documents (list of Documents): ``Document``\s present in this project.
    """
    STATUS_UNPROCESSED = 0
    STATUS_PREPROCESSING = 1
    STATUS_DONE = 2

    STATUS_NAMES = {
        STATUS_UNPROCESSED: "Not yet procesed.",
        STATUS_PREPROCESSING: "Preprocessing.",
        STATUS_DONE: "Preprocessed."
    }

    # Attributes
    name = db.Column(db.String)
    path = db.Column(db.String)
    status = db.Column(db.Integer, default=STATUS_UNPROCESSED)

    # Active project indicator
    active_project = None

    # Relationships
    sentences = db.relationship("Sentence", backref="project", lazy="dynamic")
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
    properties = db.relationship("Property",
        backref="project", lazy="dynamic")
    users = association_proxy("project_users", "user",
        creator=lambda user: ProjectsUsers(user=user))

    def is_processable(self):
        """Check if this project can be processed.
        """
        if (self.status == self.STATUS_UNPROCESSED and len(self.document_files) > 0 and
                len(self.structure_files) > 0):
            return True
        return False

    def get_documents(self):
        """A method to get all the ``Document``\s that are in this project.

        Returns:
            list of ``Document``\s.
        """

        documents = []

        for document_file in self.document_files:
            documents.extend(document_file.documents)

        return documents


    def get_errors(self, start=0):
        """Return all ``ErrorLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "error")\
            .filter(Log.id > int(start))\
            .all()

    def get_warnings(self, start=0):
        """Return all ``WarningLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "warning")\
            .filter(Log.id > int(start))\
            .all()

    def get_infos(self, start=0):
        """Return all ``InfoLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self)\
            .filter(Log.type == "info")\
            .filter(Log.id > int(start))\
            .all()