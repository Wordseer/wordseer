from app import db
from .base import Base
from .project import Project
from .sentence import Sentence
from .association_objects import WordInSequence, SequenceInSentence
from .counts import SequenceCount
from sqlalchemy.ext.associationproxy import association_proxy

class Sequence(db.Model, Base):
    """A sequence of at most 4 consecutive words in a sentence.

    Some sequences are lemmatized and are not the same as they appear in the
    original sentence.

    Attributes:
        sequence (str): the sequence text
        lemmatized (bool): whether or not it is lemmatized
        has_function_words (bool): whether or not it has function words
        all_function_words (bool): whether or not it is made of all function
            words.
        length (int): the length of the sequence
        sentences (list of Sentences): ``Sentence``\s that this document appears
            in.
        words (list of Words): ``Word``\s that appear in this ``Sequence``.
        sentence_count (int): the number of sentences this sequence appears in
        document_count (int): the number of documents this sequence appears in

    Relationships:
        belongs to: sentence
    """

    # Attributes

    sequence = db.Column(db.String, index=True)
    lemmatized = db.Column(db.Boolean, index=True)
    has_function_words = db.Column(db.Boolean, index=True)
    all_function_words = db.Column(db.Boolean, index=True)
    length = db.Column(db.Integer, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), index=True)
    
    # Relationships

    project = db.relationship("Project")
    words = association_proxy("word_in_sequence", "word",
        creator=lambda word: WordInSequence(word=word))

    # Scoped Pseudo-relationships

    @property
    def sentences(self):
        """Retrieves sentences that contain this sequence within the scope of
        the current active project.
        """

        return Sentence.query.join(SequenceInSentence).join(Sequence).\
            filter(SequenceInSentence.project==Project.active_project).\
            filter(SequenceInSentence.sequence_id==self.id).all()

    def get_counts(self, project=None):

        # project argument assigned active_project if not present
        if project == None:
            project = Project.active_project

        return SequenceCount.fast_find_or_initialize(
            "sequence_id = %s and project_id = %s" % (self.id, project.id),
            sequence_id = self.id, project_id = project.id)

    def add_word(self, word, project=None, force=True):
        """Add a word to this sequence within the scope of the project
        """

        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        word_in_sequence = WordInSequence(
            word = word,
            sequence = self,
            project = project
        )
        word_in_sequence.save(force=force)

        return word_in_sequence

    def __repr__(self):
        return "<Sequence {0}>".format(self.sequence)

