from app import db
from .base import Base

class Ngram(db.Model, Base):
    count = db.Column(db.Integer)
    has_stop_words = db.Column(db.Boolean)
    words = db.relationship("Word",
        secondary="words_in_ngrams",
        backref="ngrams")
    text = db.Column(db.String)

    def __init__(self, **kwargs):
        self.count = 0
        super(Ngram, self).__init__(**kwargs)

