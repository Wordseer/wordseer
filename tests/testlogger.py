"""
Tests for the Logger class.
"""

import unittest

from app import db
import database
from lib.wordseerbackend.wordseerbackend import logger
from app.models.log import Log

class LoggerTests(unittest.TestCase):
    """Run tests on the Logger class.
    """
    def setUp(self):
        """Clean the database.
        """
        database.restore_cache()

    def test_log(self):
        """Test the log() method. These tests assume that get() works.
        """
        logger.log("logtest", "true", logger.REPLACE)
        self.failUnless(logger.get("logtest") == "true")

        logger.log("logtest", "false", logger.UPDATE)
        self.failUnless(logger.get("logtest") == "true [false] ")

    def test_get(self):
        """Test the get() method.
        """
        entry = Log(item_value="true", log_item="logtest")
        db.session.merge(entry)
        db.session.commit()
        self.failUnless(logger.get("logtest") ==
            Log.query.filter(Log.log_item == "logtest").all()[0].item_value)

        self.failUnless(logger.get("fakerandomname") == "")

