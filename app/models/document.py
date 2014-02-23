from app.models import Base
from app.models.datatypes import *

class Document(Base):

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    title = Column(String, index = True)
    source = Column(String)

    # Relationships
    unit = relationship("Unit", backref=backref("document", uselist=False))
