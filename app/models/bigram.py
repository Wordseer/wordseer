"""Bigrams are collections of two words. They are how WordSeer handles
sequences.
"""

from app import db
from .base import Base

class Bigram(db.Model, Base):
    """A bigram consists of two words, one primary word and one secondary word.

    Between them is some distance which is less than or equal to five words;
    the secondary word may be anywhere in relation to the primary word.
    """

    def __init__(self, word, secondary_word):
        """Instantiate a bigram.

        Arguments:
            word (Word): The primary word
            secondary_word (Word): The secondary word
        """
        self.word = word
        self.secondary_word = secondary_word
        self.

