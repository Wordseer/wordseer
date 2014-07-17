from app import db
from base import Base

class Unit(db.Model, Base):
    """A model representing a unit (or segment) of text.

    This can be either a section or chapter of a document, an act in a play, or
    anything that is made of sentences.

    Units are hierarchical; one unit can contain many children units.

    Attributes:
        type (str): the unit type (document, section, etc.).
        number (int): a sequencing number (e.g. 2 for chapter 2).
        parent (Unit): The ``Unit`` that owns this ``Unit``.
        children (list of Units): ``Unit``s that this ``Unit`` owns.
        sentences (list of Sentences): ``Sentences`` found in this ``Unit``.
        properties (list of Properties): Metadata for this ``Unit``.
        name (str): A name for this ``Unit``.

    Relationships:
      has one: parent
      has many: children (Unit), sentences, properties
    """

    # Attributes
    # We need to redefine ID here for the children relationship
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))
    number = db.Column(db.Integer, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    name = db.Column(db.String)

    # Relationships
    children = db.relationship("Unit", backref=db.backref("parent",
        remote_side=[id]))
    sentences = db.relationship("Sentence", backref="unit")
    properties = db.relationship("Property", backref="unit")

    __mapper_args__ = {
        "polymorphic_identity": "unit",
        "polymorphic_on": type
    }

    def __repr__(self):
        """Return a string representation of a unit, which is its type followed
        by its ordering number.
        """

        return "<Unit: " + " ".join([str(self.type),
            str(self.number)]) + ">"

