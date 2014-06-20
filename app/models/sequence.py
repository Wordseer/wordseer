from app import db
from base import Base
from association_objects import WordInSequence, SequenceInSentence
from sqlalchemy.ext.associationproxy import association_proxy

class Sequence(db.Model, Base):
    """A sequence of at most 4 consecutive words in a sentence.

    Some sequences are lemmatized and are not the same as they appear in the
    original sentence.

    Attributes:
      sequence (str): the sequence text
      lemmatized (bool): whether or not it is lemmatized
      has_function_words (bool): whether or not it has function words
      all_function_words (bool): whether or not it is made of all function words
      length (int): the length of the sequence
      sentence_count (int): the number of sentences this sequence appears in
      document_count (int): the number of documents this sequence appears in

    Relationships:
      belongs to: sentence
    """

    # Attributes

    sequence = db.Column(db.String, index=True)
    lemmatized = db.Column(db.Boolean)
    has_function_words = db.Column(db.Boolean)
    all_function_words = db.Column(db.Boolean)
    length = db.Column(db.Integer, index=True)
    sentence_count = db.Column(db.Integer, index=True)
    document_count = db.Column(db.Integer, index=True)

    # Relationships

    sentences = association_proxy("sequence_in_sentence", "sentence",
        creator=lambda sentence: SequenceInSentence(sentence=sentence)
    )
    words = association_proxy("word_in_sequence", "word",
        creator=lambda word: WordInSequence(word=word)
    )
