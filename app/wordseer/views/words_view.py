from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class WordsView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()
        
        if "project_id" in keys:

            project = Project.query.get(params["project_id"])
            part_of_speech = params["pos"][0]
            position = params["start"][0]
            limit = params["limit"][0]

            words = project.frequent_words(part_of_speech, position, limit)

            results = []

            for word in words:
                results.append({
                    "word": word.lemma,
                    "count": word.sentence_count,
                    "is_lemmatized": 1
                })

            print(results)
            return jsonify(results = results)

    def post(self):
        pass

    def delete(self, property_id):
        pass

    def put(self, property_id):
        pass
        
register_rest_view(
    WordsView,
    wordseer,
    'words_view',
    'word',
    parents=["project"],
)