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
    @classmethod
    def setUpClass(cls):
        common.reset_db()
        cls.word1 = Word(word="foo", lemma="bar")
        cls.word2 = Word(word="foo", lemma="baz")
        cls.word3 = Word(word="bar", lemma="bar")
        cls.word4 = Word(word="baz", lemma="qux")

        db.session.add_all([cls.word1, cls.word2, cls.word3, cls.word4])
        db.session.commit()

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

        variant_ids = utils.get_lemma_variant_ids("foo")

        assert variant_ids.sort() == [self.word1.id, self.word2.id,
            self.word3.id].sort()

    def test_get_lemma_variants(self):
        """Test get_lemma_variants()
        """

        variants = utils.get_lemma_variants("foo")

        assert variants.sort() == [self.word1.word, self.word2.word,
            self.word3.word].sort()

