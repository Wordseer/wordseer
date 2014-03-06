import sys, os, unittest

sys.path.insert(0, os.path.dirname(__file__))

suite = unittest.TestLoader().discover('tests')
results = unittest.TextTestRunner(verbosity=2).run(suite)
