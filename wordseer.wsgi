import sys
import site

# use the virtualenv
site.addsitedir('/projects/wordseer/flask_demo/venv/lib/python2.7/site-packages')

# update the path
base_path = '/projects/wordseer/flask_demo/'
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# load the wordseer app
from wordseer import app as application