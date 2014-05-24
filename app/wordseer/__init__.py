"""Blueprint for the WordSeer interface.

This interface allows users to interact with the actual wordseer application.
"""
import os

from flask import Blueprint

wordseer = Blueprint('wordseer', __name__,
    template_folder='templates',
    static_folder="static",
    static_url_path=os.path.dirname(__file__))

from . import views
from . import models

