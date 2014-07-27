"""Word models.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from .base import Base
from .association_objects import WordInSentence
from .association_objects import WordInSequence
from .mixins import NonPrimaryKeyEquivalenceMixin

class Word(db.Model, Base, NonPrimaryKeyEquivalenceMixin):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
        word (str): The word.
        lemma (str): The word's lemma.
        part_of_speech (str): The part of speech of the word.
        sentences (list of Sentences): The ``Sentences`` that this ``Word`` is
            in. This relationship is described by ``WordInSentence``.
        sequences (list of Sequences): The ``Sequences`` that this ``Word`` is
            in. This relationship is described by ``WordInSequence``.
        governor_dependencies (list of Dependencies): The ``Dependency``\s in
            which this ``Word`` is a governor.
        dependent_dependencies (list of Dependencies): The ``Dependency``\s in
            which this ``Word`` is a dependent.

    Relationships:
        has many: sentences
    """

    # Attributes

    word = db.Column(db.String, index=True)
    lemma = db.Column(db.String, index=True)
    part_of_speech = db.Column(db.String, index=True)
    parse_id = db.Column(db.Integer, db.ForeignKey("parse_products.id"))

    # Relationships

    sentences = association_proxy("word_in_sentence", "sentence",
        creator=lambda sentence: WordInSentence(sentence=sentence))

    sequences = association_proxy("word_in_sequence", "sequence",
        creator=lambda sequence: WordInSequence(sequence=sequence))

    def __repr__(self):
        """Representation string for words, showing the word.
        """

        return "<Word: " + str(self.word) + ">"

