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
        sentence = Sentence(text="The quick brown fox jumped over the lazy dog",
            tagged=[TaggedWord(lemma="the", word="the"),
                TaggedWord(lemma="quick", word="quick"),
                TaggedWord(lemma="brown", word="brown"),
                TaggedWord(lemma="fox", word="fox"),
                TaggedWord(lemma="jump", word="jumped"),
                TaggedWord(lemma="over", word="over"),
                TaggedWord(lemma="the", word="the"),
                TaggedWord(lemma="lazy", word="lazy"),
                TaggedWord(lemma="dog", word="dog")],
            id=1,
            document_id=2)
        result = self.seq_proc.process(sentence)

def split_sequences(sequences):
    """The output of the sequencer can be split into four different types of
    sequences for ease of checking: Sequences of words, sequences of lemmas,
    sequences of words without stops, and sequences of lemmas without stops.
    This method performs that split.

    :param list sequences: A list of Sequences to split.
    :result dict: A dict, in the format ["words"|"lemmas"]["stops"|"nostops"]
    """

    result = {
        "words": {
            "stops": [],
            "nostops": []
        },
        "lemmas": {
            "stops": [],
            "nostops": []
        }
    }
    
    for sequence in sequences:
        if sequence.is_lemmatized:
            if sequence.has_function_words:
                result["lemmas"]["stops"].append(sequence)
            else:
                result["lemmas"]["nostops"].append(sequence)
        elif:
            if sequence.has_function_words:
                result["words"]["stops"].append(sequence)
                #TODO: finish
