from app.models import Base
from app.models.datatypes import *

class Metadata(Base):

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    property_name = Column(String, index = True)
    property_value = Column(String, index = True)

    # Relationships
    unit = relationship("Unit", backref=backref("metadata", uselist=False))
