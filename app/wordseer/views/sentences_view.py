from flask.views import MethodView
from flask.json import jsonify, dumps, loads
from flask import request

from app import app
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view
from app.wordseer.helpers import parse_phrase_strings

class SentencesView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)        
        query = Query.query.get(params["query_id"])
        if query:
            results = []
            for sentence in query.sentences:
                results.append({
                    "sentence": sentence.text,
                    "sentence_id": sentence.id,
                    "document_id": sentence.document_id,
                    "sentence_set": " ".join(sentence.sets)                 
                })
            return jsonify(results = results)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass
        

register_rest_view(
    SentencesView,
    wordseer,
    'sentences_view',
    'sentence',
    parents=["project", "document", "unit"],
)
