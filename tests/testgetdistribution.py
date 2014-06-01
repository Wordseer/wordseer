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
        cls.getdistribution = GetDistribution()

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
        # Set up the trial units
        unit1 = Unit()
        unit2 = Unit()
        sent1 = Sentence(unit = unit2)
        sent2 = Sentence(unit = unit1)
        sent3 = Sentence(unit = unit2)
        sent4 = Sentence(unit = unit1)

        db.session.add_all([unit1, unit2, sent1, sent2, sent3, sent4])

        # Run the SUT
        result = self.getdistribution.get_dimensions(unit1.id)

        assert result.min == sent2
        assert result.max == sent4
        assert result.length == 2

