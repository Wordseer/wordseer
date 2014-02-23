from app.models import Base
from app.models.datatypes import *

class WordInSentence(Base):

    # Schema
    word_id = Column(Integer, ForeignKey('word.id'))
    sentence_id = Column(Integer, ForeignKey('sentence.id'))
