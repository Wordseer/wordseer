"""
Tests for the Logger class.
"""
import database
from models import Log
import logger
import unittest

class LoggerTests(unittest.TestCase):
    """Run tests on the Logger class.
    """
    def setUp(self):
        """Set up the Logger and the Database.
        """
        self.db = database.Database()

    def test_log(self):
        """Test the log() method. These tests assume that get() works.
        """
        logger.log("logtest", "true", "replace")
        self.failUnless(logger.get("logtest") == "true")

        logger.log("logtest", "false", "update")
        self.failUnless(logger.get("logtest") == "true [false] ")

    def test_get(self):
        #TODO: write for new get
        """Test the get() method. 
        """
        entry = Log(item_value="true", log_item="logtest")
        self.db.session.merge(entry)
        self.db.session.commit()
        self.failUnless(logger.get("logtest") ==
            self.db.session.query(Log).filter(Log.log_item == "logtest").\
            all()[0].item_value)

        self.failUnless(logger.get("fakerandomname") == "")