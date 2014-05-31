"""Tests for getdistribution.py
"""

import unittest

from app import app
from app import db
from app.uploader.models import Sentence
from app.uploader.models import Unit
from app.wordseer.views.getdistribution import GetDistribution

class TestGetDistribution(unittest.TestCase):
    """Tests for the GetDistribution view.
    """

    def setUp(self):
        open(app.config["SQLALCHEMY_DATABASE_PATH"], "w").close()
        db.create_all()

    @classmethod
    def setUpClass(cls):
        """Set up the test client.
        """
        cls.client = app.test_client()
        cls.url = "/getdistribution"

    def test_arguments(self):
        """Test to make sure the correct arguments are required.
        """

        arguments = [
            "narrative=foo",
            "type=foo"
        ]

        #TODO: better way
        for argument in arguments:
            result = self.client.get(self.url + "?" + argument)
            assert result.status_code == 400

    def test_get_dimensions(self):
        """Test the get_dimensions method.
        """
        unit1 = Unit()
        unit2 = Unit()
        sent1 = Sentence(unit = unit1)


