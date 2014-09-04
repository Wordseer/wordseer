"""
Unit tests for the helpers module.
"""

import unittest
import pdb

import mock

from app import app
from app import db
from app.models import Word
from app.wordseer import helpers
import database

@unittest.skip("Needs reworking based on how the views are written.")
class TestUtils(unittest.TestCase):
    """Test the helpers module.
    """
    @classmethod
    def setUpClass(cls):
        database.clean()
        cls.word1 = Word(lemma="bar")
        cls.word2 = Word(lemma="baz")
        cls.word3 = Word(lemma="bar")
        cls.word4 = Word(lemma="qux")

        db.session.add_all([cls.word1, cls.word2, cls.word3, cls.word4])
        db.session.commit()

    def test_table_exists(self):
        """Test to make sure that table_exists recognizes every existing table
        and not tables that don't exist.
        """

        for table_name in db.metadata.tables.keys():
            self.failUnless(helpers.table_exists(table_name))

        self.failIf(helpers.table_exists("foobarbazfoo"))

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

        assert expected == helpers.remove_spaces_around_punctuation(sentence)

    @mock.patch("app.wordseer.helpers.request", autospec=True)
    def test_get_word_ids_from_sequence_set(self, mock_request):
        """Test the get_word_ids_from_sequence_set method with
        all_word_forms on.
        """

        mock_request.args = {"all_word_forms": "off"}

        with app.test_request_context():
            word_ids = helpers.get_word_ids_from_sequence_set(
                self.sequenceset1.id)

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id,
            self.word4.id])

    @unittest.skip("Do we even need this?")
    @mock.patch("app.wordseer.helpers.request", autospec=True)
    def test_lemmatize_get_word_ids_from_sequence_set(self, mock_request):
        """Test the get_word_ids_from_sequence_set method with
        all_word_forms off.
        """

        mock_request.args = {"all_word_forms": "on"}

        with app.test_request_context():
            word_ids = helpers.get_word_ids_from_sequence_set(
                self.sequenceset1.id)

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id,
            self.word3.id, self.word4.id])

    @mock.patch("app.wordseer.helpers.request", autospec=True)
    def test_get_word_ids_from_surface_word(self, mock_request):
        """Test the get_word_ids_from_surface_word method with all_word_forms
        off.
        """

        mock_request.args = {"all_word_forms": "off"}

        with app.test_request_context():
            word_ids = helpers.get_word_ids_from_surface_word("fo*")

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id])

    @unittest.skip("Waiting for clarification")
    @mock.patch("app.wordseer.helpers.request", autospec=True)
    def test_get_word_ids_from_surface_word(self, mock_request):
        """Test the get_word_ids_from_surface_word method with all_word_forms
        on.
        """

        mock_request.args = {"all_word_forms": "on"}

        with app.test_request_context():
            word_ids = helpers.get_word_ids_from_surface_word("fo*")

        pdb.set_trace()

        assert sorted(word_ids) == sorted([self.word1.id, self.word2.id])

