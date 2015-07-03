"""Describes a file that stores one or more documents..
"""

from app import db
from .base import Base

class DocumentFile(db.Model, Base):
    """Every file uploaded or present on the filesystem is stored in a
    ``DocumentFile``. Every ``DocumentFile`` can contain one or more
    ``Document``\s.

    Attributes:
        path (str): The location of the file as an absolute path.
        projects (list of Projects): The projects that this file belongs to.
        documents (list of Documents): The ``Document``\s present in this
            ``DocumentFile``.
    """

    path = db.Column(db.String)
    documents = db.relationship("Document", backref="document_file", cascade="all, delete-orphan")

