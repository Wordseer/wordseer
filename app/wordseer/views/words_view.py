from flask.views import MethodView
from flask.json import jsonify, dumps, loads
from flask import request
from sqlalchemy import func
from sqlalchemy.sql.expression import asc, desc

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
            
            results = self.get_frequent_words(params, project, part_of_speech,
                is_lemmatized = False)
            results.extend(self.get_frequent_words(params, project,
                part_of_speech, is_lemmatized = True))
            return jsonify(results = results)

    def get_frequent_words(
        self, params, project, part_of_speech, is_lemmatized):
        words_query = db.session.query(
            Word.id,
            Word.lemma.label("lemma"),
            Word.surface.label("word"),
            func.count(Sentence.id).label("sentence_count"),
            func.count(Sentence.document_id.distinct()).label("document_count")).\
            group_by(Word.lemma if is_lemmatized else Word.surface).\
            filter(Word.part_of_speech.like("%" + part_of_speech + "%")).\
            filter(Sentence.project_id == project.id).\
            filter(Word.id == WordInSentence.word_id).\
            filter(Sentence.id == WordInSentence.sentence_id).\
            order_by(desc("sentence_count"))
        if "query_id" in params:
            query = Query.query.get(params["query_id"])
            words_query = words_query.filter(
                SentenceInQuery.query_id == query.id)
            words_query = words_query.filter(
                SentenceInQuery.sentence_id == Sentence.id)

        results = []
        for word in words_query:
            results.append({
                "id": "." + str(word.id) if is_lemmatized else str(word.id),
                "word": word.lemma if is_lemmatized else word.word,
                "is_lemmatized": 1 if is_lemmatized else 0,
                "count": word.sentence_count,
                "document_count": word.document_count
            })
        return results

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass

register_rest_view(
    WordsView,
    wordseer,
    'words_view',
    'word',
    parents=["project"],
)
