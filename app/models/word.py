from app.models import Base
from app.models.datatypes import *

class Word(Base):

    # Schema
    word = Column(String, index = True)
