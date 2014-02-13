from app.models import Base
from app.models.datatypes import *

class Unit(Base):
    unit_type = Column(String(64), index = True)
    number = Column(Integer, index = True)
