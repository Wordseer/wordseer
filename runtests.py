import os
import sys
import unittest

os.environ['FLASK_ENV'] = "testing"

import tests

print "blah"
print os.environ['FLASK_ENV']

suite = unittest.TestLoader().loadTestsFromModule(tests)
results = unittest.TextTestRunner(verbosity=2).run(suite)
