"""Models for property metadata.
"""

from app import db
from base import Base

class PropertyMetadata(db.Model, Base):
    """Describes ``Property`` objects of the same type: metametadata, if you
    will.

    ``Property``\s must have additional data attached to it to describe to
    wordseer what should be done with it.

    Attributes:
        type (str): The type of these ``Property``\s (string, int, date, etc.)
        is_category (boolean): whether this property can be used to sort and
            filter items.
        display_name (str): The name of the property that this object is
            describing; this is the same as the ``name`` of the
            ``Property`` object described.
        display (boolean): If True, then the ``Property`` objects described
            by this object should have their names and values described in
            the reading view on the frontend.
    """

    property_name = db.Column(db.String)
    data_type = db.Column(db.String)
    date_format = db.Column(db.String)
    is_category = db.Column(db.Boolean)
    display_name = db.Column(db.String)
    display = db.Column(db.Boolean, default=False)
    unit_type = db.Column(db.String)
