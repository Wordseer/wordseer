"""Models to describe grammatical relationships.
"""

from app import db
from .base import Base

class GrammaticalRelationship(db.Model, Base):
    """A grammatical relationship between two words.

    This indicates the type of relationship between the governor and the
    dependent in the dependency model.

    Attributes:
        name (str): the name of the relationship
        dependency (Dependency): The ``Dependency`` this
            ``GrammaticalRelationship`` belongs to.

    Relationships:
        belongs to: dependency
    """

    # Attributes

    name = db.Column(db.String)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete='CASCADE'))

    # Relationships

    dependencies = db.relationship('Dependency', backref="grammatical_relationship")

    def __repr__(self):
        """Return a string representation of this ``GrammaticalRelationship``.
        """

        return str(self.name)
