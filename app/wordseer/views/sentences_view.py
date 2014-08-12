from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class SentencesView(MethodView):

    def get(self, **kwargs):
        pass

    def post(self):
        pass

    def delete(self, property_id):
        pass

    def put(self, property_id):
        pass
        

register_rest_view(
    SentencesView,
    wordseer,
    'sentences_view',
    'sentence',
    parents=["document", "unit"],
)