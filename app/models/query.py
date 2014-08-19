from .base import Base
from app import db

class Query(db.Model, Base):
    """A model to store queries
    """

    # Attributes

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Relationship

    project = db.relationship("Project")
    user = db.relationship("User")