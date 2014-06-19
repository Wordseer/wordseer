"""Blueprint for the WordSeer interface.

This interface allows users to interact with the actual wordseer application.
"""
import os

from flask import Blueprint
static_url = os.path.dirname(__file__)#Problem with this static absolute path. changed to relative
wordseer = Blueprint('wordseer', __name__,
    template_folder='templates',
    static_folder="static",
    static_url_path="/app/wordseer/")

from .views import *
