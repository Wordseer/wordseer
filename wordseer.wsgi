import os

# use the virtualenv
activate_this = os.path.abspath('venv/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# load the wordseer app
# TODO: pass along a port config?
from wordseer import app as application
