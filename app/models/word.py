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
from .counts import WordCount
from .mixins import NonPrimaryKeyEquivalenceMixin

class Word(db.Model, Base, NonPrimaryKeyEquivalenceMixin):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
        lemma (str): The word's lemma.
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

    id = db.Column(db.Integer, primary_key=True, index=True)
    lemma = db.Column(db.String, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    sentences = association_proxy("word_sentences", "sentence",
        creator=lambda word: WordInSentence(sentence=sentence))

    #Pseudo-relationships
    @property
    def sequences(self):
        """Retrieves sequences that contain this word within the scope of the
        current active project.
        """
        return self.get_sequences()

    def get_sequences(self, project=None):
        if not project:
            project = Project.active_project

        return Sequence.query.join(WordInSequence).\
            filter(WordInSequence.project==project).\
            filter(WordInSequence.word==self).all()

    def get_counts(self, project=None):

        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        return WordCount.fast_find_or_initialize(
            "word_id = %s and project_id = %s" % (self.id, project.id),
            word_id = self.id, project_id = project.id)

    def __repr__(self):
        """Representation string for words, showing the word.
        """

        return "<Word: " + str(self.lemma) + ">"

