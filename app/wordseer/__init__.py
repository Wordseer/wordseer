"""Initialize the WordSeer website.
"""

from flask import Blueprint

uploader = Blueprint('wordseer', __name__, template_folder='templates')

from . import views
from . import models
