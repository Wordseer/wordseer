from app import db
from base import Base

class Property(db.Model, Base):
    """A model representing a property of a unit.

    Metadata about units are stored as properties, which have a link to the
    unit it belongs to. Any form of metadata can be assigned to a unit, making
    them extensible and flexible.

    Attributes:
      unit_id: the primary key of the unit it belongs to
      name: the name of the property
      value: the value of the property

    Relationships:
      belongs to: unit

    """

    # Attributes
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    name = db.Column(db.String, index=True)
    value = db.Column(db.String, index=True)

    def __repr__(self):
        """Representation string for properties, showing the property name
        """

        return "<Property: " + str(self.name) + ">"
