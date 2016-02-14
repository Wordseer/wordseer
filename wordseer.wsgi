import sys

# use the virtualenv
activate_this = '/projects/wordseer/flask-demo/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

# update the path
base_path = '/projects/wordseer/flask_demo/'
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# load the wordseer app
from wordseer import app as application