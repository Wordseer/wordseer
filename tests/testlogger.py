"""Tests for the Logger class.
"""

import unittest

import database
from app import db
from app.models.log import Log
from app.models.project import Project
from app.preprocessor import logger

class LoggerTests(unittest.TestCase):
    """Run tests on the Logger class.
    """
    def setUp(self):
        """Clean the database.
        """
        database.clean()

    def test_log(self):
        """Test the log() method. These tests assume that get() works.
        """
        project = Project()
        project.save()

        logger.log(project, "logtest", "true", logger.REPLACE)
        self.failUnless(logger.get(project, "logtest") == "true")

        logger.log(project, "logtest", "false", logger.UPDATE)
        self.failUnless(logger.get(project, "logtest") == "true [false] ")

    def test_get(self):
        """Test the get() method.
        """
        project = Project()
        project.save()

        entry = Log(project=project, item_value="true", log_item="logtest")
        entry.save()

        self.failUnless(logger.get(project, "logtest") ==
            Log.query.filter(Log.log_item == "logtest").all()[0].item_value)

        self.failUnless(logger.get(project, "fakerandomname") == "")

