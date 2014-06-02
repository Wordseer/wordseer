"""Tests for the wordfrequencies module.
"""

import json
import unittest

from app import app
from app import db
from app.uploader.models import Sentence
from app.uploader.models import Word

class TestGetWordFrequencies(unittest.TestCase):
    """Tests for the get_word_frequencies view.
    """

    @classmethod
    def setUpClass(cls):
        """Clear the database and set up the querying client.
        """
        db.create_all()
        cls.client = app.test_client()
        cls.url = "/word-frequencies/get-frequent-words"

    def test_arguments(self):
        """Make sure that arguments are handled properly.
        """
        result = self.client.get(self.url)
        assert result.status_code == 400

        result = self.client.get(self.url + "?" + "words=foo")
        assert result.status_code == 400

        result = self.client.get(self.url + "?" + "page=2")
        assert result.status_code != 400

        result = self.client.get(self.url + "?" + "page=2&word=foo")
        assert result.status_code != 400

    def test_get_word_frequency_page(self):
        """Test the get_word_frequency_page method.
        """

        words = []

        s1 = Sentence(text="foo")
        s2 = Sentence(text="foor")
        s3 = Sentence(text="bar")
        for i in range(0, 25):
            words.append(Word(word="foo", sentences=[s1]))
            words.append(Word(word="foor", sentences=[s2]))

        words.append(Word(word="bar", sentences=[s3]))

        db.session.add_all(words)
        db.session.commit()

        result = self.client.get(self.url + "?" + "words=foo&page=2")

        words = json.loads(result.data)

        print words

