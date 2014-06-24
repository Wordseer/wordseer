import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class GetSentence(View):
    """Utilities and functions for getting a specific set of sentences"""
    pass
