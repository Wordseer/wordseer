from .sentence import Sentence
from .project import Project
from .association_objects import DependencyInSentence
from .counts import DependencyCount
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from base import Base

class Dependency(db.Model, Base):
    """A representation of the grammatical dependency between two words.

    Each dependency is comprised of a governor, a dependent, and a grammatical
    relationship.

    Attributes:
        grammatical_relationship (GrammaticalRelationship): The
            ``GrammaticalRelationship`` which describes the relationship between
            the governor and the dependent.
        governor (Word): The governor ``Word``.
        dependent (Word): The dependent ``Word``.
        sentence_count (int): the number of sentences this appears in
        document_count (int): the number of documents this appears in
        sentences (list of Sentences): ``Sentence``\s that this dependency is
            in.

    Relationships:
        Has one: dependent (Word), governor (Word), grammatical relationship
        Has many: sentences
    """

    # Attributes

    grammatical_relationship_id = db.Column(
        db.Integer, db.ForeignKey("grammatical_relationship.id"))
    governor_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    dependent_id = db.Column(db.Integer, db.ForeignKey("word.id"))

    # Relationships

    grammatical_relationship = db.relationship(
        "GrammaticalRelationship", backref="dependency")

    governor = db.relationship("Word", foreign_keys=[governor_id])

    dependent = db.relationship("Word", foreign_keys=[dependent_id])

    # Scoped Pseudo-relationships

    @property
    def sentences(self):
        """Retrieves all sentences that contain this dependency, within
        the scope of the current active project.
        """

        return Sentence.query.join(DependencyInSentence).join(Dependency).\
            filter(DependencyInSentence.project==Project.active_project).\
            filter(DependencyInSentence.dependency==self).all()

    def get_counts(self, project=None):

        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        return DependencyCount.find_or_create(
            dependency_id = self.id,
            project_id = project.id,
        )

    def __repr__(self):
        """Representation string for the dependency
        """

        #rel = str(self.grammatical_relationship.name)
        #gov = str(self.governor.word)
        #dep = str(self.dependent.word)

        return "<Dependency: " + str(self.grammatical_relationship) + "(" + \
            str(self.governor) + ", " + str(self.dependent) + ") >"

