"""Tests for the ``app.wordseer.models`` module.
"""

import unittest

from app import db
from app.wordseer.models import Set
from app.wordseer.models import SequenceSet
from app.wordseer.models import SentenceSet
from app.wordseer.models import DocumentSet
from common import reset_db

class TestSets(unittest.TestCase):
    """Test all the different ``Set`` models.
    """

    @classmethod
    def setUpClass(cls):
        reset_db()

        cls.set = Set()
        cls.sequenceset = SequenceSet()
        cls.sentenceset = SentenceSet()
        cls.documentset = DocumentSet()

        db.session.add_all([cls.set, cls.sequenceset, cls.sentenceset,
            cls.documentset])
        db.session.commit()

    def test_set(self):
        """Test to make sure that ``Set`` is working.
        """

        sets = db.session.query(Set).all()

        assert len(sets) == 4
        assert self.set in sets

    def test_sequenceset(self):
        """Test the ``SequenceSet`` model.
        """

        sets = db.session.query(SequenceSet).all()

        assert len(sets) == 1
        assert self.sequenceset in sets

    def test_sentenceset(self):
        """Test the ``SentenceSet`` model.
        """

        sets = db.session.query(SentenceSet).all()

        assert len(sets) == 1
        assert self.sentenceset in sets

    def test_documentset(self):
        """Test the ``DocumentSet`` model.
        """

        sets = db.session.query(DocumentSet).all()

        assert len(sets) == 1
        assert self.documentset in sets

