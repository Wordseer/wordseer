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

    @unittest.skip("not functional")
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
        for arg1 in request_args:
            for arg2 in request_args:
                for arg3 in request_args:
                    for arg4 in request_args:
                        for arg5 in request_args:
                            for arg6 in request_args:
                                request = self.client.get(self.url + "?")
        request = self.client.get(self.url + "?instance=foo")
        assert request.status_code == 400

