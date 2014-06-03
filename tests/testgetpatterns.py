"""Tests for the getpatterns module.
"""

import json
import unittest

from app import app
from app import db
from app.uploader.models import Dependency
from app.uploader.models import Sentence

class TestGetPatterns(unittest.TestCase):
    """Tests for the get_patterns view.
    """
    @classmethod
    def setUpClass(cls):
        """Set up the testing client.
        """
        cls.client = app.test_client()
        cls.url = "/getpatterns"

        db.create_all()
        s1 = Sentence()
        s2 = Sentence()
        s3 = Sentence()
        d1 = Dependency(gov_index=0, dep_index=1, governor="foo1",
            dependent="bar1", sentences=[s1,s2,s3], relationship="foo")
        d2 = Dependency(gov_index=2, dep_index=3, governor="foo2",
            dependent="bar2", sentences=[s1,s2,s3], relationship="dep")
        d3 = Dependency(gov_index=2, dep_index=1, governor="foo3",
            dependent="bar3", sentences=[s1, s3], relationship="foo")
        d4 = Dependency(gov_index=4, dep_index=4, governor="foo4",
            dependent="bar4", sentences=[s2], relationship="foo")

        db.session.add_all([s1, s2, s3, d1, d2, d3])
        db.session.commit()

    def test_get_patterns_arguments(self):
        """Make sure required arguments are required.
        """
        response = self.client.get(self.url + "?" + "start=1&end=2")
        assert response.status_code == 400

        response = self.client.get(self.url + "?" + "sentence=foo")
        assert response.status_code == 400

        response = self.client.get(self.url + "?" + "sentence=1")
        assert response.status_code != 400

    def test_get_patterns_response(self):
        """Make sure the response is well-formed.
        """
        response = self.client.get(self.url + "?" + "sentence=1")

        response_dict = json.loads(response.data)

        assert len(response_dict["results"]) == 3

        for result in response_dict["results"]:
            assert len(result) == 4
            assert set(result.keys()) == set(["id", "gov", "dep", "relation"])

    def test_get_patterns_result(self):
        """Make sure the query and logic is working properly.
        """
        min_index = 0
        max_index = 3
        sent_index = 1

        response = self.client.get(self.url + "?" + "start=" + str(min_index) +
            "&end=" + str(max_index) + "&sentence=" + str(sent_index))
        response_dict = json.loads(response.data)

        for result in response_dict["results"]:
            dependency = db.session.query(Dependency).\
                filter(Dependency.id == result["id"]).one()
            assert result["relation"] != "dep"
            assert result["gov"] == dependency.governor
            assert result["dep"] == dependency.dependent
            assert result["relation"] == dependency.relationship

            assert dependency.gov_index <= max_index
            assert dependency.dep_index <= max_index
            assert dependency.gov_index >= min_index
            assert dependency.dep_index >= min_index

