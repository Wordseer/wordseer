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
        self.log = logger.Logger()
        self.db = database.Database()

    def test_log(self):
        """Test the log() method. These tests assume that get() works.
        """
        self.log.log("logtest", "true", "replace")
        self.failUnless(self.log.get("logtest") == "true")

        self.log.log("logtest", "false", "update")
        self.failUnless(self.log.get("logtest") == "true [false] ")

    def test_get(self):
        """Test the get() method. 
        """
        entry = Log(item_value="true", log_item="logtest")
        self.db.session.merge(entry)
        self.db.session.commit()
        self.failUnless(self.log.get("logtest") == self.db.session.query(Log).filter(Log.log_item == "logtest").all()[0].item_value)