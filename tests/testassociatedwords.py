"""Tests for the GetAssociatedWords view.
"""

import unittest

from app import app

class TestGetAssociatedWords(unittest.TestCase):
    """Test the GetAssociatedWords view.
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test client.
        """
        cls.client = app.test_client()
        cls.url = "/word-frequencies/word-frequencies"

    @unittest.skip("Find another way")
    def test_arguments(self):
        """Test to make sure that errors are shown when necessary arguments
        are not supplied.
        """

        request_args = [
            "instance=foo",
            "collection=foo",
            "statistics=foo",
            "timing=foo",
            'phrases={"foo":1}',
            'metadata={"foo":1}',
            'searches={"foo":1}'
        ]

        # this is very very very bad
        for i in range(0, len(request_args)):
            args = "&".join(request_args[:i] + request_args[(i + 1):])
            request = self.client.get(self.url + "?" + args)
            assert request.status_code == 400

