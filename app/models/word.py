from app import db
from base import Base
from association_objects import WordInSentence, WordInSequence
from sqlalchemy.ext.associationproxy import association_proxy

class Word(db.Model, Base):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
      word (str): the word

    Relationships:
      has many: sentences
    """

    # Attributes

    word = db.Column(db.String, index=True)
    lemma = db.Column(db.String, index=True)
    tag = db.Column(db.String, index=True)

    # Relationships

    sentences = association_proxy("word_in_sentence", "sentence",
        creator=lambda sentence: WordInSentence(sentence=sentence)
    )

    sequences = association_proxy("word_in_sequence", "sequence",
        creator=lambda sequence: WordInSequence(sequence=sequence)
    )

    def __repr__(self):
        """Representation string for words, showing the word.
        """

        return "<Word: " + self.word + ">"


