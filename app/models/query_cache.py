from .base import Base
from .sentence import Sentence
from app import db

class QueryCache(db.Model, Base):
    """A model to store cached results from queries
    """

    # Attributes

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    sentence_ids = db.Column(db.String)
    matches = db.Column(db.Integer)
    matched_searches = db.Column(db.Integer)


    # Relationship

    project = db.relationship("Project")

    @property
    def sentences(self):
        ids = [ int(id) for id in self.sentence_ids.split(",") ]
        return [ Sentence.query.get(id) for id in ids ]