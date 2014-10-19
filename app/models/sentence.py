"""Sentence models.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from .base import Base
from .project import Project
from .association_objects import DependencyInSentence
from .association_objects import SequenceInSentence
from .association_objects import WordInSentence
from .counts import WordCount, DependencyCount, SequenceCount

class Sentence(db.Model, Base):
    """A model representing a sentence.

    The sentence model is treated like "leaf" units. It has a link to its
    parent unit as well as the top-level document. Sentences contain words
    (the model), and also stores its own raw text, for use in search results.

    Attributes:
        unit (Unit): The ``Unit`` containing this sentence.
        document (Document): the ``Document`` (top-level unit) to which this
            sentence belongs to.
        text (str): The raw text of the sentence.
        sequences (list of Sequences): ``Sequence``\s present in this sentence.
            This relationship is described with ``SequenceInSentence``.
        dependencies (list of Dependencies): ``Dependency``\s present in this
            sentence. This relationship is described with
            ``DependencyInSentence``.
        properties (list of Propertys): ``Property``\s associated with this
            ``Sentence``.
        words (list of Words): ``Word``\s in this ``Sentence``.

    Relationships:
        belongs to: unit, document
        has many: words, sequences, dependencies
    """

    # Attributes

    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))
    text = db.Column(db.Text, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    # Relationships

    words = association_proxy("word_in_sentence", "word",
        creator=lambda word: WordInSentence(word=word))

    sequences = association_proxy("sequence_in_sentence", "sequence",
        creator=lambda sequence: SequenceInSentence(sequence=sequence))

    dependencies = association_proxy("dependency_in_sentence", "dependency",
        creator=lambda dependency: DependencyInSentence(dependency=dependency))

    document = db.relationship("Document", foreign_keys=[document_id],
        backref="all_sentences")

    properties = association_proxy("property_of_sentence", "property",
        creator=lambda property: PropertyOfSentence(property=property))

    def __repr__(self):
        """Representation of the sentence, showing its text.

        NOTE: could be trucated to save print space
        """

        return "<Sentence: " + str(self.text) + ">"

    def add_word(self, word, position=None, space_before="",
        surface=None, project=None, force=True):
        """Add a word to the sentence by explicitly creating the association
        object.

        Arguments:
            word (Word): The ``Word`` that should be added to this ``Sentence``.

        Keyword Arguments:
            position (int): The position (0-indexed) of ``word`` in this
                ``Sentence``.
            space_before (str): The space before ``word``, if any.
            project (Project): The ``Project`` that scopes this relationship

        Returns:
            WordInSentence: The association object that associates this
                ``Sentence`` and ``word``.
        """

        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        word_in_sentence = WordInSentence(
            word=word,
            surface=surface,
            project=project,
            sentence=self,
            position=position,
            space_before=space_before,
        )

        word_in_sentence.save(force=force)

        return word_in_sentence

    def add_dependency(self, dependency, governor_index=None,
        dependent_index=None, project=None, force=True):
        """Add a dependency to the sentence by explicitly creating the
        association object.

        Arguments:
            dependency (Dependency): The ``Dependency`` in this relationship.

        Keyword Arguments:
            governor_index (int): Position (0-indexed) of the governor in this
                ``Sentence``. Default is ``None``.
            dependent_index (int): Position (0-indexed) of the dependent in this
                ``Sentence``. Default is ``None``.

        Returns:
            DependencyInSentence: The association object that associates this
                ``Sentence`` and ``dependency``.
        """

        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        dependency_in_sentence = DependencyInSentence(
            dependency=dependency,
            sentence=self,
            project=project,
            document=self.document,
            governor_index=governor_index,
            dependent_index=dependent_index
        )

        dependency_in_sentence.save(force=force)

        return dependency_in_sentence

    def add_sequence(self, sequence, position=None, project=None, force=True):
        """Add a ``Sequence`` to the ``Sentence`` by explicitly creating the
        association object.

        Arguments:
            sequence (Sequence): The ``Sequence`` to associate with this
                ``Sentence``.

        Keyword Arguments:
            position (int): The position (0-indexed) of this ``Sequence`` in
                this ``Sentence``. Default is ``None``.

        Returns:
            SequenceInSentence: The association object that associates this
            ``Sentence`` and ``sequence``.
        """
        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        sequence_in_sentence = SequenceInSentence(
            sequence=sequence,
            sentence=self,
            project=project,
            document=self.document,
            position=position
        )

        sequence_in_sentence.save(force=force)

        return sequence_in_sentence

    @staticmethod
    def apply_grammatical_search_filter(search_queryt_dict, sentence_query):
        """ Gets the sentences that contain the dependency relations specified
        by the query parameters.

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
            A list of Sentence objects that contain the dependencies specified
            by the query parameters.
        """
        sentence_query = Sentence.query
        return sentence_query

