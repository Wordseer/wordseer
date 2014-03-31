"""
Tests for the SequenceProcessor class.
"""
from document.taggedword import TaggedWord
from document.sentence import Sentence
from sequence.sequenceprocessor import (SequenceProcessor, Sequence,
    join_tws, LEMMA, WORD)
import unittest
import pprint

class SequenceProcessorTests(unittest.TestCase):
    """Tests for SequenceProcessor.
    """
    def setUp(self):
        """Obtain a SequenceProcessor.
        """
        self.seq_proc = SequenceProcessor("")

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

    @unittest.skip("Need clarification")
    def test_process(self):
        """Test process()
        """
        sentence = Sentence(text="The quick brown fox jumped over the lazy dog",
            tagged=[TaggedWord(lemma="the", word="the"),
                TaggedWord(lemma="fox", word="fox"),
                TaggedWord(lemma="jump", word="jumped"),
                TaggedWord(lemma="over", word="over"),
                TaggedWord(lemma="the", word="the"),
                TaggedWord(lemma="dog", word="dog")],
            id=1,
            document_id=2)
        result = self.seq_proc.process(sentence)
        sequences = split_sequences(result)
        sequence_sequences = get_sequence_text(sequences)

        # Create four lists of sequences based on the categories and then
        # check the output
        key = {
            "words": {
                "stops": [
                    "the",
                    "the fox",
                    "the fox jumped",
                    "the fox jumped over",
                    "fox",
                    "fox jumped",
                    "fox jumped over",
                    "fox jumped over the",
                    "jumped",
                    "jumped over",
                    "jumped over the dog",
                    "over",
                    "over the",
                    "over the dog"],
                "nostops": [
                    "fox",
                    "fox jumped",
                    "fox jumped dog",
                    "jumped",
                    "jumped dog",
                    "dog"]
            },
            "lemmas": {
                "stops": [
                    "the",
                    "the fox",
                    "the fox jump",
                    "the fox jump over",
                    "fox jump over",
                    "fox jump over the",
                    "jump over",
                    "jump over the dog",
                    "over",
                    "over the",
                    "over the dog",
                    "the",
                    "the dog"],
                "nostops": [
                    "fox jump dog",
                    "jump dog",
                    "fox",
                    "fox jump",
                    "jump",
                    "dog"]
            }
        }

        #pprint.pprint(sequence_sequences)
        self.failUnless(sequence_sequences == key)
        

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
        seq_type = "words"
        if sequence.is_lemmatized:
            seq_type = "lemmas"

        stops = "nostops"
        if sequence.has_function_words:
            stops = "stops"

        result[seq_type][stops].append(sequence)

    return result

def get_sequence_text(sequences):
    """Given the result of split_sequences, replace every Sequence with the text
    contained in it.

    :param dict sequences: the output of split_sequences
    """
    for seq_type, stop_types in sequences.items():
        for stop_type, seq_list in stop_types.items():
            for i in range(0, len(seq_list)): #TODO: more pythonic?
                sequences[seq_type][stop_type][i] = seq_list[i].sequence

    return sequences
