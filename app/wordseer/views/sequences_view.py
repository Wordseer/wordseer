from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request
from sqlalchemy import func
from sqlalchemy.sql.expression import asc, desc

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class SequencesView(MethodView):
    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        project = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])    
        if project is None:
            return "[]"
    
        # TODO(silverasm): in the case where there's no query_id, use the
        # sequence count table directly.
        length = int(params["length"][0])
        sequence_query = None;
        if "query_id" in params:
            query = Query.query.get(params["query_id"])
            sequence_query = db.session.query(
                Sequence.id,
                Sequence.lemmatized.label("lemmatized"),
                Sequence.has_function_words.label("has_function_words"),
                Sequence.sequence.label("sequence"),
                func.count(Sentence.id).label("sentence_count"),
                func.count(Sentence.document_id.distinct()).label("document_count")).\
                group_by(Sequence.id).\
                filter(Sentence.project_id == project.id).\
                join(SentenceInQuery,
                     SentenceInQuery.sentence_id == Sentence.id).\
                filter(SentenceInQuery.query_id == query.id).\
                filter(Sequence.all_function_words == False).\
                filter(Sequence.length == length).\
                filter(Sequence.id == SequenceInSentence.sequence_id).\
                filter(Sentence.id == SequenceInSentence.sentence_id)
        else:
            # There's no query id, we just want the most frequent sequences in
            # the whole collection.
            sequence_query = FrequentSequence.query.\
                filter(FrequentSequence.project_id == project.id)

        sequence_query = sequence_query.order_by(desc("sentence_count"))
        results = []
        for sequence in sequence_query:
            result = {
                "count": sequence.sentence_count,
                "sentence_count": sequence.sentence_count,
                "sequence": sequence.sequence,
                
            }
            if "query_id" in params:
                result["id"] = sequence.id
                result["has_function_words"] = 1 if sequence.has_function_words else 0
                result["lemmatized"] = 1 if sequence.lemmatized else 0
                result["length"] = length
                result["document_count"] = sequence.document_count
            else:
                result["id"] = sequence.sequence_id

                
                

            results.append(result)

        return jsonify(results = results)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass


class ContainingSequencesView(MethodView):
    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        project = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])    
        if project is None:
            return "[]"
        
        sequences = SequenceInSentence.query.\
            filter(SequenceInSentence.sentence_id ==
                   params.get("sentence_id")[0]).\
            filter(SequenceInSentence.position ==
                   params.get("start_position")[0]).\
            subquery()

        counts = db.session.query(
            Sequence.id.label("id"),
            Sequence.sequence.label("sequence"),
            func.count(SequenceInSentence.sentence_id.distinct()).label("sentence_count")).\
        filter(SequenceInSentence.sequence_id == Sequence.id).\
        filter(Sequence.lemmatized == False).\
        join(sequences, SequenceInSentence.sequence_id ==
                       sequences.c.sequence_id).\
        group_by(Sequence.id).\
        order_by(asc(Sequence.length))


        results = []
        for sequence in counts:
            results.append(sequence._asdict());
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

register_rest_view(
    ContainingSequencesView,
    wordseer,
    'containing_sequences_view',
    'containing_sequence',
    parents=["project"],
)
