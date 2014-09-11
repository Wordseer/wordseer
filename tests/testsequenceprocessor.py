"""
Tests for the SequenceProcessor class.
"""

import mock
import unittest

from app.models.document import Document
from app.models.project import Project
from app.models.word import Word
from app.models.bigram import Bigram
from app.models.sentence import Sentence
from app.preprocessor.sequenceprocessor import SequenceProcessor
import database
import pdb

class SequenceProcessorTests(unittest.TestCase):
    """Tests for SequenceProcessor.
    """
    def setUp(self):
        """Obtain a SequenceProcessor.
        """
        database.clean()
        self.project = mock.create_autospec(Project)
        self.sequence_processor = SequenceProcessor(self.project)
        self.sequence_processor.project_logger = mock.MagicMock()

    def test_process(self):
        """Test the process method.
        """
        self.sequence_processor.get_bigrams = mock.MagicMock()
        mock_sentences = []
        get_bigrams_calls = []
        sentence1 = Sentence()
        sentence2 = Sentence()
        sentence3 = Sentence()
        for i in range(0, 10):
            mock_sentence = Sentence()
            for j in range(0, 4):
                mock_word = Word()
                mock_sentence.words.append(mock_word)
                mock_word.sentences.extend([sentence1, sentence2, sentence3])
                get_bigrams_calls.append(mock.call(mock_sentence, mock_word, j))


            mock_sentences.append(mock_sentence)

        self.project.get_sentences.return_value = mock_sentences

        pdb.set_trace()

        self.sequence_processor.process()

        self.sequence_processor.get_bigrams.assert_has_calls(get_bigrams_calls)

    @mock.patch("app.preprocessor.sequenceprocessor.Bigram", autospec=True)
    def test_get_bigrams(self, mock_bigram):
        """Test the get_bigrams method.
        """
        sentence = Sentence(words=[
            Word(lemma="The"),
            Word(lemma="quick"),
            Word(lemma="brown"),
            Word(lemma="the"),
            Word(lemma="fox"), # Query word
            Word(lemma="jumped"),
            Word(lemma="over"),
            Word(lemma="the"),
            Word(lemma="lazy"),
            Word(lemma="dog")])

        pass

