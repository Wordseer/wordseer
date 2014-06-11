"""
Unit tests for the utils module.
"""

import unittest

from app import app
from app import db
from app.uploader.models import Word
from app.wordseer import utils
import common

class TestUtils(unittest.TestCase):
    """Test the utils module.
    """
    def setUp(self):
        common.reset_db()

    def test_table_exists(self):
        """Test to make sure that table_exists recognizes every existing table
        and not tables that don't exist.
        """

        for table_name in db.metadata.tables.keys():
            self.failUnless(utils.table_exists(table_name))

        self.failIf(utils.table_exists("foobarbazfoo"))

    def test_remove_spaces_around_punctuation(self):
        """Test to make sure that spaces are removed properly in
        remove_spaces_around_punctuation.
        """

        before_set = set(app.config["PUNCTUATION_NO_SPACE_BEFORE"])
        after_set = set(app.config["PUNCTUATION_NO_SPACE_AFTER"])

        only_before = before_set - after_set
        only_after = after_set - before_set
        both = before_set & after_set

        sentence = (
            u" x " +
            u" x ".join(only_after) +
            u" x " +
            u" x ".join(only_before) +
            u" x " +
            u" x ".join(both)
        )
        expected = (
            u" x " +
            u"x ".join(only_after) +
            u"x" +
            u" x".join(only_before) +
            u" x" +
            u"x".join(both)
        )

        assert expected == utils.remove_spaces_around_punctuation(sentence)

    def test_get_lemma_variant_ids(self):
        """Test get_lemma_variant_ids().
        """

        word1 = Word(word="foo", lemma="bar")
        word2 = Word(word="foo", lemma="baz")
        word3 = Word(word="bar", lemma="bar")
        word4 = Word(word="baz", lemma="qux")

        db.session.add_all([word1, word2, word3, word4])
        db.session.commit()

        variant_ids = utils.get_lemma_variant_ids("foo")

        assert variant_ids.sort() == [word1.id, word2.id, word3.id].sort()

