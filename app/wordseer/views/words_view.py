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
            
            # TODO(silverasm): when there's no query_id use the word counts
            # table directly.
            results = self.get_frequent_words(params, project, part_of_speech,
                is_lemmatized = False)
            results.extend(self.get_frequent_words(params, project,
                part_of_speech, is_lemmatized = True))
            return jsonify(results = results)

    def get_frequent_words(
        self, params, project, part_of_speech, is_lemmatized):
        words_query = None
        like_query = "%" + part_of_speech + "%"
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
            sentence_count_expr = WordCount.sentence_count
            document_count_expr = WordCount.document_count
            if is_lemmatized:
                sentence_count_expr = func.sum(WordCount.sentence_count)
                document_count_expr = func.sum(WordCount.document_count)

            words_query = db.session.query(
                Word.id,
                Word.lemma.label("lemma"),
                Word.surface.label("word"),
                sentence_count_expr.label("sentence_count"),
                document_count_expr.label("document_count")).\
            filter(WordCount.project_id == project.id).\
            filter(WordCount.word_id == Word.id).\
            filter(Word.part_of_speech.like(like_query))

            if is_lemmatized:
                words_query = words_query.group_by(Word.lemma)
        
        words_query = words_query.order_by(desc("sentence_count"))

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
