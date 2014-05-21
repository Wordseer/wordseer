"""Initialize the WordSeer website.
"""

from flask import Blueprint

wordseer = Blueprint('wordseer', __name__, template_folder='templates')

from . import views
from . import models
