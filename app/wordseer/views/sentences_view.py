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
        keys = params.keys()

        Project.active_project = Project.query.get(params["project_id"])

        phrases = params["phrases"][0]

        if phrases:
            phrases = loads(phrases)
            sequence_texts = parse_phrase_strings(phrases)

            sequences = list()

            for text in sequence_texts:
                sequences.append(Sequence.query.filter_by(sequence=text).first())

            sentences = set()

            for sequence in sequences:
                for sentence in sequence.sentences:
                    sentences.add(sentence)

            results = []

            for sentence in sentences:
                results.append({
                    "sentence": sentence.text,
                    "sentence_id": sentence.id,
                    "document_id": sentence.document_id,
                    "sentence_set": "testing"
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