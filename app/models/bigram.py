"""Bigrams are collections of two words. They are how WordSeer handles
sequences.
"""
import math
import pdb
from app import db
from .base import Base
from .association_objects import BigramOffset
from .project import Project

class Bigram(db.Model, Base):
    """A bigram consists of two words, one primary word and one secondary word.

    Between them is some distance which is less than or equal to five words;
    the secondary word may be anywhere in relation to the primary word.
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    secondary_word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    frequency = db.Column(db.Integer, default=0)
    stage = db.Column(db.Integer, default=0)
    strength = db.Column(db.Float)
    spread = db.Column(db.Integer)
    interesting = db.Column(db.Boolean, default=False)

    word = db.relationship("Word", foreign_keys=word_id)
    secondary_word = db.relationship("Word", foreign_keys=secondary_word_id)

    offsets = db.relationship("BigramOffset", backref="bigram",
        order_by="BigramOffset.offset")

    def __init__(self, word, secondary_word, project=None):
        """Instantiate a bigram.

        Arguments:
            word (Word): The primary word
            secondary_word (Word): The secondary word
        """
        if not project:
            project = Project.active_project

        self.frequency = 0
        self.word = word
        self.secondary_word = secondary_word
        self.offsets = [BigramOffset(offset=i, bigram=self,
            project_id=project.id) for i in range(-5, 0) + range(1, 6)]

    def get_offset(self, offset):
        """Get the BigramOffset object that corresponds to a given offset
        for this Bigram.

        Arguments:
            offset (int): The offset to get.

        Returns:
            BigramOffset: The correct BigramOffset object.
        """
        if offset < 0:
            return self.offsets[offset + 5]
        elif offset > 0:
            return self.offsets[offset + 4]
        else:
            raise ValueError("Offset cannot be 0")

    def add_instance(self, offset, sentence, force=True):
        """Add an occurrence of this bigram.

        Arguments:
            offset (int): The offset of ``secondary_word`` from ``word``.
            sentence (Sentence): The sentence where this instance ocurrs.

        Returns:
            BigramOffset: The modified BigramOffset object.
        """
        #TODO: should run differently if this is a stage 1 bigram

        bigram_offset = self.get_offset(offset)
        bigram_offset.add_sentence(sentence, force)

        self.frequency += 1

        return bigram_offset

    def __repr__(self):
        """Return a string representation of this bigram.
        """
        return "<Bigram | primary: %s | secondary: %s >" % (self.word,
            self.secondary_word)

    def get_strength(self):
        """Get the strength of this word pair.

        Strength is defined the frequency of this pair minus the average
        average frequency of the primary word in this pair (f-bar) divided by
        the standard deviation around f-bar.

        Returns:
            float: The strength of this word pair, also known as ki,
        """
        try:
            return (self.frequency - self.get_fbar()) / self.get_sigma()
        except ZeroDivisionError:
            return 0.0

    def get_spread(self):
        """This method returns the shape of the histogram showing the frequency
        of ``secondary_word`` versus ``offset``.

        If the value (known as ui) returned by this function is small, then
        the histogram will tend to be flat and ``secondary_word`` has an equal
        chance of appearing with any offset relative to ``word``. If it is
        large, then the histogram will tend to have peaks at certain offsets.

        The formula is the average variance of all offsets.

        Returns:
            float: ui, a value described above.
        """
        ui = 0.0

        for offset in self.offsets:
            difference = offset.frequency - (self.frequency / 10)
            ui += (difference * difference)

        return ui / 10

    def get_interesting_offsets(self, k1=1):
        """Return offsets that are interesting to look at. If a certain
        offset is unusually favored, it will be returned by this method.

        Arguments:
            k1 (int): Threshhold above which distances are interesting.

        Returns:
            list of BigramOffsets: A list of BigramOffsets representing
            interesting offsets.
        """

        min_peak = (self.frequency / 10) + (k1 * math.sqrt(self.get_spread()))

        distances = []

        for offset in self.offsets:
            if offset.frequency > min_peak:
                offset.interesting = True
                distances.append(offset)

        return distances

    def get_number_of_offsets(self):
        """Return the number of unique offsets that this bigram has.

        Returns:
            int: between 1 and 10, inclusive.
        """
        num_offsets = 0
        for offset in self.offsets:
            if len(offset.sentences) > 0:
                num_offsets += 1

    def get_fbar(self):
        """Get the average frequency of this bigram.

        Defined as the number of ocurrences of this bigram divided by
        the number of bigrams with the same primary word.

        Returns:
            float
        """
        # Works
        bigrams = self.query.filter(Bigram.word == self.word).all()
        total_ocurrences = 0.0

        for bigram in bigrams:
            total_ocurrences += bigram.frequency

        total_bigrams = len(bigrams)
        return total_ocurrences / total_bigrams

    def get_sigma(self):
        """Get the standard deviation around f-bar, that is, the standard
        deviation of bigram frequencies.

        Returns:
            float
        """
        # Works
        fbar = self.get_fbar()
        bigrams = self.query.filter(Bigram.word == self.word).all()

        squared_diffs = 0.0
        #pdb.set_trace()
        for bigram in bigrams:
            x = bigram.frequency - fbar
            squared_diffs += (x * x)

        return math.sqrt(squared_diffs / len(bigrams))

    def pass_stage_one(self):
        self.strength = self.get_strength()
        self.spread = self.get_spread()
        offsets = self.get_interesting_offsets()
        self.stage = 1
        if offsets:
            self.frequency = 0
            self.interesting = True
        for offset in offsets:
            self.frequency += offset.frequency

