"""
Tests for the SequenceProcessor class.
"""
from document.taggedword import TaggedWord
from document.sentence import Sentence
from sequence.sequenceprocessor import SequenceProcessor, join_tws, LEMMA, WORD
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
        self.failUnless(join_tws(self.words, " ", LEMMA) == self.string)

    def test_join_words(self):
        """Test join_words()
        """
        self.failUnless(join_tws(self.words, " ", WORD) == self.string)

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

    def test_process(self):
        """Test process()
        """
        sentence = Sentence(text="first second third",
            tagged=self.words,
            id=1,
            document_id=2)
        result = self.seq_proc.process(sentence)
        for seq in result:
            print seq.sequence
            