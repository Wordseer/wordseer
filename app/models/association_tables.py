from app.models import Base
from app.models.datatypes import *

# Many-to-many table between this model and the Word model
word_in_sentence = Table("word_in_sentence", Base.metadata,
    Column('word_id', Integer, ForeignKey('word.id')),
    Column('sentence_id', Integer, ForeignKey('sentence.id'))
)
