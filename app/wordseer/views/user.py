import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class User(View):
    """Called by signIn in user.js in service of
    all main application web pages, to handle user authentication.
    Returns a JSON object containing user data or information about
    errors."""
    pass
