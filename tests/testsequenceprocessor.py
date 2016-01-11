"""
Tests for the SequenceProcessor class.
"""

import mock
import unittest

from app.models.association_objects import WordInSentence
from app.models.document import Document
from app.models.project import Project
from app.models.word import Word
from app.models.sentence import Sentence
from app.preprocessor.sequenceprocessor import (SequenceProcessor,
    join_words, LEMMA, WORD)
import database

class SequenceProcessorTests(unittest.TestCase):
    """Tests for SequenceProcessor.
    """
    def setUp(self):
        """Obtain a SequenceProcessor.
        """
        database.clean()
        self.project = Project()
        self.seq_proc = SequenceProcessor(self.project)


    def test_join_words(self):
        """Test join_words()
        """
        words_in_sentences = [WordInSentence(surface="First", word=Word(lemma="first")),
            WordInSentence(surface="Second", word=Word(lemma="second")),
            WordInSentence(surface="Third", word=Word(lemma="third"))]
        lemma_string = "first second third"
        word_string = "First Second Third"

        assert join_words(words_in_sentences, LEMMA) == lemma_string
        assert join_words(words_in_sentences, WORD) == word_string

    def test_remove_stops(self):
        """Test remove_stops()
        """
        with_stops = [WordInSentence(word=Word(lemma=".")),
            WordInSentence(word=Word(lemma="a")),
            WordInSentence(word=Word(lemma="around")),
            WordInSentence(word=Word(lemma="empire")),
            WordInSentence(word=Word(lemma="!")),
            WordInSentence(word=Word(lemma="Camelot")),
            WordInSentence(word=Word(lemma="theirs")),
            WordInSentence(word=Word(lemma="who")),
            WordInSentence(word=Word(lemma="wouldst")),
            WordInSentence(word=Word(lemma="were")),
            WordInSentence(word=Word(lemma="again"))]

        without_stops = [WordInSentence(word=Word(lemma="empire")),
            WordInSentence(word=Word(lemma="Camelot"))]
        result = self.seq_proc.remove_stops(with_stops)

        without_stops_words = [word.word for word in without_stops]
        result_words = [word.word for word in result]

        removed = self.seq_proc.remove_stops(with_stops)

        self.failUnless(result_words == without_stops_words)

    def test_process(self):
        """Test process()
        """
        document = Document()
        sentence = Sentence(text="The quick brown fox jumped over the lazy dog",
            document=document, project = self.project)
        words = [
            Word(lemma="the", surface="the"),
            Word(lemma="fox", surface="fox"),
            Word(lemma="jump", surface="jumped"),
            Word(lemma="over", surface="over"),
            Word(lemma="the", surface="the"),
            Word(lemma="dog", surface="dog")]
        for index, word in enumerate(words): 
            word.save()
            sentence.add_word(word, index+1, " ", word.surface, self.project)
        sentence.save()

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

        print sequence_sequences
        # TODO: the seqproc isn't making phrases of words separated by a stopword,
        # but this code expects it to.
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

