#!/usr/bin/env python
"""
A file to automatically run tests with the proper FLASK_ENV setting. It also
creates the database file and runs ``database.cache()``.
"""

import os
import sys
import unittest
import pdb
from nose.core import main

os.environ['FLASK_ENV'] = "testing"
import database

def run_tests():
    database.reset()
    database.cache()
    results = main()
    pdb.set_trace()
    if results.wasSuccessful():
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    run_tests()

