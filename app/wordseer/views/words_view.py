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

        project = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
        if project is None:
            return # 500 error
        part_of_speech = params["pos"][0]
        results = self.get_frequent_words(params, project, part_of_speech,
            is_lemmatized = False)
        results.extend(self.get_frequent_words(params, project,
            part_of_speech, is_lemmatized = True))
        return jsonify(results = results)

    def get_frequent_words(
        self, params, project, part_of_speech, is_lemmatized):
        words_query = None
        like_query = part_of_speech + "%"
        if "query_id" in params:
            query = Query.query.get(params["query_id"])
            words_query = db.session.query(
                Word.id,
                Word.lemma.label("lemma"),
                Word.surface.label("word"),
                func.count(Sentence.id).label("sentence_count"),
                func.count(Sentence.document_id.distinct()).label("document_count")).\
                group_by(Word.lemma if is_lemmatized else Word.surface).\
                filter(Sentence.project_id == project.id).\
                join(SentenceInQuery,
                    SentenceInQuery.sentence_id == Sentence.id).\
                filter(SentenceInQuery.query_id == query.id).\
                filter(Word.part_of_speech.like(like_query)).\
                filter(Word.id == WordInSentence.word_id).\
                filter(Sentence.id == WordInSentence.sentence_id)
        else:
            # There's no query id, we just want the most frequent words in
            # the whole collection.
            is_lemmatized = False
            count_docs = False

            words_query = FrequentWord.query.\
                filter(FrequentWord.project_id == project.id).\
                filter(FrequentWord.pos.like(like_query))
        
        words_query = words_query.order_by(desc("sentence_count"))

        results = []
        for word in words_query:
            result = {
                "word": word.lemma if is_lemmatized else word.word,
                "is_lemmatized": 1 if is_lemmatized else 0,
                "count": word.sentence_count,
            }
            if "query_id" in params: 
                result["id"] = "." + str(word.id) if is_lemmatized else str(word.id)
                result["document_count"] = word.document_count
            else: 
                result["id"] = str(word.word_id)

            results.append(result)
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
