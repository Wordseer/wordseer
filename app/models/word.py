"""Word models.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from .base import Base
from .project import Project
from .sentence import Sentence
from .sequence import Sequence
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

    # Scoped Pseudo-relationships

    @property
    def sentences(self):
        """Retrieves sentences that contain this word within the scope of the
        current active project.
        """

        return Sentence.query.join(WordInSentence).join(Word).\
            filter(WordInSentence.project==Project.active_project).\
            filter(WordInSentence.word==self).all()

    @property
    def sequences(self):
        """Retrieves sequences that contain this word within the scope of the
        current active project.
        """

        return Sequence.query.join(WordInSequence).join(Word).\
            filter(WordInSequence.project==Project.active_project).\
            filter(WordInSequence.word==self).all()

    def __repr__(self):
        """Representation string for words, showing the word.
        """

        return "<Word: " + str(self.word) + ">"

