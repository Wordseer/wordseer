#!/usr/bin/env python
"""
A file to automatically run tests with the proper FLASK_ENV setting.
"""

import os
import unittest

os.environ['FLASK_ENV'] = "testing"

import tests

suite = unittest.TestLoader().loadTestsFromModule(tests)
results = unittest.TextTestRunner(verbosity=2).run(suite)
