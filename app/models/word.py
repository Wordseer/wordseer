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
from .sets import SequenceSet
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
    surface = db.Column(db.String, index=True)
    part_of_speech = db.Column(db.String)

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

    @staticmethod
    def get_matching_word_ids(query_string=None, is_set_id=False):
        """Returns a list of Word ids that match the given query"""
        word_ids = []
        if is_set_id:
            sequences = SequenceSet.query.get(query_string).sequences
            for sequence in sequences:
                if sequence.length == 1:
                    for word in sequence.words:
                        word_ids.append(word.id)
        if query_string is not None:
            w = Word.query.filter(
                Word.surface.like(query_string.lower()))
            for word in w:
                word_ids.append(word.id)
        return word_ids

    @staticmethod
    def apply_non_grammatical_search_filter(search_query_dict, sentence_query):
        """ Gets the sentences that contain the query specified by the given
        parameters.

        Arguments:
            search_query_dict (dict): A dictionary representation of a search
                query. Contains the keys:
                    - gov: The governor word in the case of grammatical search
                        or the string search query in the case of a
                        non-grammatical search. 
                    - dep: The dependent word in the case of grammatical search
                        (ignored for a non-grammatical search)
                    - relation: The grammatical relationships. A space-separated
                        list of grammatical relationship identifiers. If this
                        is "" or not present, the search is assumed to be
                        non-grammatical.
        Returns:
            A query object with sentences that match the given query parameters.
        """
        if "gov" in search_query_dict:
            matching_word_ids = Word.get_matching_word_ids(
                search_query_dict["gov"],
                is_set_id = search_query_dict["govtype"] != "word")    
            sentence_query = sentence_query.\
                join(WordInSentence,
                    WordInSentence.sentence_id == Sentence.id).\
                filter(WordInSentence.word_id.in_(matching_word_ids))
            return sentence_query
        return sentence_query

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

