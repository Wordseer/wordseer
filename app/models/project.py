"""Models for projects.
"""
from app import db
from base import Base
from .log import Log

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
        secondary="document_files_in_projects", backref="projects"
    )
    structure_files = db.relationship("StructureFile", backref="project")
    logs = db.relationship("Log", backref="project")

    def get_documents(self):
        """A method to get all the ``Document``\s that are in this project.

        Returns:
            list of ``Document``\s.
        """

        documents = []

        for document_file in self.document_files:
            documents.extend(document_file.documents)

        return documents

    def get_errors(self):
        """Return all ``ErrorLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "error").all()

    def get_warnings(self):
        """Return all ``WarningLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "warning").all()

    def get_infos(self):
        """Return all ``InfoLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "info").all()

