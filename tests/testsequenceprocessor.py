"""
Tests for the SequenceProcessor class.
"""
from document.taggedword import TaggedWord
from sequence.sequenceprocessor import SequenceProcessor
import unittest

class SequenceProcessorTests(unittest.TestCase):
    """Tests for SequenceProcessor.
    """
    def setUp(self):
        """Obtain a SequenceProcessor.
        """
        self.seq_proc = SequenceProcessor("", True)

        self.words = [TaggedWord(lemma="first", word="first"),
            TaggedWord(lemma="second", word="second"),
            TaggedWord(lemma="third", word="third")]
        self.string = "first second third"

    def test_join_lemmas(self):
        """Test join_lemmas()
        """
        self.failUnless(self.seq_proc.join_tws(self.words, " ", "lemma") ==
            self.string)

    def test_join_words(self):
        """Test join_words()
        """
        self.failUnless(self.seq_proc.join_tws(self.words, " ", "word") ==
            self.string)

    def test_remove_stops(self):
        """Test remove_stops()
        """
        with_stops = [TaggedWord(word="."),
            TaggedWord(word="a"),
            TaggedWord(word="around"),
            TaggedWord(word="empire"),
            TaggedWord(word="!"),
            TaggedWord(word="Camelot"),
            TaggedWord(word="theirs"),
            TaggedWord(word="who"),
            TaggedWord(word="wouldst"),
            TaggedWord(word="were"),
            TaggedWord(word="again")]

        without_stops = [TaggedWord(word="empire"),
            TaggedWord(word="Camelot")]

        self.failUnless(self.seq_proc.remove_stops(with_stops) == without_stops)