"""
Tests for the SequenceProcessor class.
"""

import mock
import unittest

from app.models.document import Document
from lib.wordseerbackend.wordseerbackend.database.readerwriter import ReaderWriter
from app.models.word import Word
from app.models.sentence import Sentence
from lib.wordseerbackend.wordseerbackend.sequence.sequenceprocessor import (SequenceProcessor,
    join_tws, LEMMA, WORD)

class SequenceProcessorTests(unittest.TestCase):
    """Tests for SequenceProcessor.
    """
    def setUp(self):
        """Obtain a SequenceProcessor.
        """
        mock_reader_writer = mock.create_autospec(ReaderWriter)
        self.seq_proc = SequenceProcessor(mock_reader_writer)

        self.words = [Word(lemma="first", word="first"),
            Word(lemma="second", word="second"),
            Word(lemma="third", word="third")]
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
        with_stops = [Word(word="."),
            Word(word="a"),
            Word(word="around"),
            Word(word="empire"),
            Word(word="!"),
            Word(word="Camelot"),
            Word(word="theirs"),
            Word(word="who"),
            Word(word="wouldst"),
            Word(word="were"),
            Word(word="again")]

        without_stops = [Word(word="empire"),
            Word(word="Camelot")]

        removed = self.seq_proc.remove_stops(with_stops)

        self.failUnless(self.seq_proc.remove_stops(with_stops) == without_stops)

    def test_process(self):
        """Test process()
        """
        document = Document()
        sentence = Sentence(text="The quick brown fox jumped over the lazy dog",
            words=[Word(lemma="the", word="the"),
                Word(lemma="fox", word="fox"),
                Word(lemma="jump", word="jumped"),
                Word(lemma="over", word="over"),
                Word(lemma="the", word="the"),
                Word(lemma="dog", word="dog")],
            id=1,
            document=document)
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
                    "fox jumped over",
                    "fox jumped over the",
                    "jumped over",
                    "jumped over the",
                    "jumped over the dog",
                    "over",
                    "over the",
                    "over the dog",
                    "the",
                    "the dog"],
                "nostops": [
                    "fox",
                    "fox jumped",
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
                    "jump over the",
                    "jump over the dog",
                    "over",
                    "over the",
                    "over the dog",
                    "the",
                    "the dog"],
                "nostops": [
                    "fox",
                    "fox jump",
                    "jump",
                    "jump dog",
                    "dog"]
            }
        }

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
        if sequence["is_lemmatized"]:
            seq_type = "lemmas"

        stops = "nostops"
        if sequence["has_function_words"]:
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
                sequences[seq_type][stop_type][i] = seq_list[i]["sequence"]

    return sequences

