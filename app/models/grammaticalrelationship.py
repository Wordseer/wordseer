"""Models to describe grammatical relationships.
"""

from app import db
from base import Base

class GrammaticalRelationship(db.Model, Base):
    """A grammatical relationship between two words.

    This indicates the type of relationship between the governor and the
    dependent in the dependency model.

    Attributes:
      name (str): the name of the relationship

    Relationships:
      belongs to: dependency
    """

    # Attributes

    name = db.Column(db.String, index=True)

    def __repr__(self):
        """Return a string representation of this ``GrammaticalRelationship``.
        """

        return str(self.name)

