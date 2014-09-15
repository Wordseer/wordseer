from flask import request
from flask.json import jsonify, dumps, loads
from flask.views import MethodView

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class SentenceView(MethodView):
    def get(self, **kwargs):
        params = dict(kwargs, **request.args)

register_rest_view(
    SentenceView,
    wordseer,
    'sentences',
    'sentence',
    parents=["project"]
)