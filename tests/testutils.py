"""
Unit tests for the Utils module.
"""

import unittest

from app import db
from app import app
from app.wordseer import utils

@unittest.skip("Not working")
class TestUtils(unittest.TestCase):
    """Test the Utils module.
    """
    def test_table_exists(self):
        """Test to make sure that table_exists recognizes every existing table
        and not tables that don't exist.
        """

        for table_name in db.metadata.tables.keys():
            self.failUnless(utils.table_exists(table_name))

        self.failIf(utils.table_exists("foobarbazfoo"))

    def test_get_name_from_relation(self):
        """Make sure that get_name_from_relation correctly recognizes all
        known relationships.
        """
        for relations, name in app.config["RELATIONS"].iteritems():
            for relation in relations:
                assert utils.get_name_from_relation(relation) == name
