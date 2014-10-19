from app import db
from base import Base

class Property(db.Model, Base):
    """A model representing a property of a unit.

    Metadata about units are stored as properties, which have a link to the
    unit it belongs to. Any form of metadata can be assigned to a unit, making
    them extensible and flexible.

    Attributes:
        unit (Unit): The ``Unit`` this ``Property`` belongs to.
        name (str): The name of the property.
        value (str): The value of the property.
        specification (str): The JSON description of this type of property.
        sentence (Sentence): The ``Sentence`` this ``Property`` belongs to.

    Relationships:
      belongs to: unit

    """

    # Attributes
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    metadata_id = db.Column(db.Integer, db.ForeignKey("property_metadata.id"))

    name = db.Column(db.String, index=True)
    value = db.Column(db.String, index=True)
    data_type = db.Column(db.String)
    date_format = db.Column(db.String)
    property_metadata = db.relationship("PropertyMetadata", backref="properties")

    def __repr__(self):
        """Representation string for properties, showing the property name
        """

        return "<Property: " + str(self.name) + ">"

