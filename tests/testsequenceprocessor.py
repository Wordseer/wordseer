"""
Tests for the SequenceProcessor class.
"""

import mock
import unittest

from app.models.document import Document
from app.models.project import Project
from app.models.word import Word
from app.models.sentence import Sentence
from app.preprocessor.sequenceprocessor import SequenceProcessor
import database

class SequenceProcessorTests(unittest.TestCase):
    """Tests for SequenceProcessor.
    """
    def setUp(self):
        """Obtain a SequenceProcessor.
        """
        database.clean()
        self.project = mock.create_autospec(Project)
        self.seq_proc = SequenceProcessor(self.project)

        self.words = [Word(lemma="first", word="first"),
            Word(lemma="second", word="second"),
            Word(lemma="third", word="third")]
        self.string = "first second third"

