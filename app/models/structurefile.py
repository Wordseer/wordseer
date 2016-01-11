"""Describes a file that stores a project's structure.
"""

from app import db
from .base import Base

class StructureFile(db.Model, Base):
    """Each structure file is stored as a ``StructureFile``.

    Attributes:
        path (str): The location of this structure file as an absolute path.
        project (Project): The project that this structure file belongs to.
    """

    path = db.Column(db.String)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete='CASCADE'))

