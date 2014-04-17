import os

from flask import Flask
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)

app.config.from_object('config')
CsrfProtect(app)

def get_filename(string):
    """
    Given a path, return the name of the file.

    Used in templates that list filenames.

    :param str string: The path to split.
    """
    return os.path.split(string)[1]

app.jinja_env.filters['get_filename'] = get_filename

from app.controllers import *
from app.models import *

#TODO: these imports are all over the place
