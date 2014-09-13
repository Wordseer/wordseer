from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class SequencesView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
            position = int(params["start"][0])
            length = int(params["length"][0])
            limit = int(params["limit"][0])

            results = []

            sequences = project.frequent_sequences(length, limit)

            for sequence in sequences:
                results.append({
                    "count": sequence.sentence_count,
                    "sequence": sequence.sequence,
                })

            return jsonify(results = results)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass


register_rest_view(
    SequencesView,
    wordseer,
    'sequences_view',
    'sequence',
    parents=["project"],
)
