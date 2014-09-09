from app import db
from .base import Base

class Ngram(db.Model, Base):
    """An Ngram is a collection of several words that co-occur with each other
    unusually frequently.

    Attributes:
        count (int): How often this Ngram occurs in its corpus.
        has_stop_words (boolean): If this Ngram contains stop words.
        words (list of Words): Words that are present in this ngram.
        text (string): The raw text of this ngram.
    """

    count = db.Column(db.Integer)
    has_stop_words = db.Column(db.Boolean)
    words = db.relationship("Word",
        secondary="words_in_ngrams",
        backref="ngrams")
    text = db.Column(db.String)

    def __init__(self, **kwargs):
        self.count = 0
        super(Ngram, self).__init__(**kwargs)

