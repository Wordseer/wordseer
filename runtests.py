#!/usr/bin/env python

import os
import sys
import unittest

os.environ['FLASK_ENV'] = "testing"

import tests

suite = unittest.TestLoader().loadTestsFromModule(tests)
results = unittest.TextTestRunner(verbosity=2).run(suite)
