#!/usr/bin/env python
"""
A file to automatically run tests with the proper FLASK_ENV setting. It also
creates the database file and runs ``database.cache()``.
"""

import os
import sys
import unittest
import pdb

os.environ['FLASK_ENV'] = "testing"
import database

if __name__ == "__main__":
    database.reset()
    database.cache()

    sys.path.insert(0, os.path.dirname(__file__))
    suite = unittest.TestLoader().discover('tests')
    results = unittest.TextTestRunner(verbosity=2).run(suite)

