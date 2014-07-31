"""Models for projects.
"""
from app import db
from base import Base

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

    # Relationships
    documents = db.relationship("Document", secondary="documents_in_projects",
            backref="projects")
    logs = db.relationship("Log", backref="project")

