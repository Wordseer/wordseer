from app.models import Base
from app.models.datatypes import *

class Document(Base):
    unit_id = Column(Integer, ForeignKey('unit.id'))
    title = Column(String, index = True)
    source = Column(String)
    unit = relationship("Unit", backref=backref("unit", uselist=False))
