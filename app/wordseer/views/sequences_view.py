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

        project = Project.query.get(params["project_id"])

        document_ids = str([ document.id for document in project.get_documents() ]).replace("[", "(").replace("]", ")")
        position = int(params["start"][0])
        length = int(params["length"][0])
        limit = int(params["limit"][0])

        # TODO: make into actual relationship and rewrite
        query = db.session.execute("""
            SELECT sequence.id, sequence.sequence, sequence.lemmatized,
                sequence.has_function_words, sequence.all_function_words,
                sequence.length, sequence.sentence_count, sequence.document_count,
                sequence_in_sentence.sentence_id
            FROM sequence INNER JOIN sequence_in_sentence
            ON sequence.id = sequence_in_sentence.sequence_id
            WHERE sequence_in_sentence.position = {0} AND
                sequence.length = {1} AND
                sequence_in_sentence.document_id IN {2}
            ORDER BY sequence.sentence_count DESC
            LIMIT {3}
        """.format(position, length, document_ids, limit))

        results = []

        for row in query.fetchall():
            results.append(dict(row))

        print(results[:5])
        return jsonify(results = results)

    def post(self):
        pass

    def delete(self, property_id):
        pass

    def put(self, property_id):
        pass
        

register_rest_view(
    SequencesView,
    wordseer,
    'sequences_view',
    'sequence',
    parents=["project"],
)

        # {
        #     "sequence_id": "216293",
        #     "sentence_id": "5258",
        #     "document_id": "5256",
        #     "start_position": "18",
        #     "id": "216293",
        #     "sequence": "slim SBF",
        #     "lemmatized": "0",
        #     "has_function_words": "0",
        #     "all_function_words": "0",
        #     "length": "2",
        #     "sentence_count": "1",
        #     "document_count": "1"
        # },