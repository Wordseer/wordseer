"""WSGI module to run wordseer on web servers
"""
import os
import sys

# use the virtualenv
activate_this = os.path.abspath('venv/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# update the path
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)
print sys.path

# load the wordseer app
from wordseer import app as application
