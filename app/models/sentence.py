from app.models import Base
from app.models.datatypes import *

class Sentence(Base):

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    text = Column(Text, index = True)

    # Relationships
    unit = relationship("Unit", backref=backref("sentences"))

    words = relationship("Word",
        secondary="word_in_sentence",
        backref="sentences"
    )
