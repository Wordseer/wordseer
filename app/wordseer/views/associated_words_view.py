from __future__ import division
import math 

from flask.views import MethodView
from flask.json import jsonify, dumps, loads
from flask import request
from sqlalchemy import func
from sqlalchemy.sql.expression import asc, desc

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class AssociatedWordsView(MethodView):

    def get_category(self, pos):
        if pos.startswith("N"):
            return "Nouns"
        elif pos.startswith("V"):
            return "Verbs"
        elif pos.startswith("J"):
            return "Adjectives"

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        project = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
        if project is None:
            return # 500 error

        # retrieve the cached query to get associated words for 
        query = None
        if "query_id" in keys:
            query = Query.query.get(params["query_id"])
            sentences = query.sentences
        if query is None:
            search_param = loads(params["search"][0])[0]
            sequence_ids = Word.get_matching_sequence_ids(search_param['gov'])
            sentences = Sentence.query.\
                filter(Sentence.project_id == project.id).\
                filter(SequenceInSentence.sequence_id.in_(sequence_ids)).\
                filter(Sentence.id == SequenceInSentence.sentence_id)

            
        associated_words = db.session.query(
            Word.id.label("id"),
            Word.part_of_speech.label("pos"),
            Word.surface.label("word"),
            func.count(WordInSentence.sentence_id.distinct()).label("count"),
            func.count(Sentence.document_id.distinct()).label("doc_count")
            ).\
        filter(WordInSentence.sentence_id.in_([sentence.id for sentence in sentences])).\
        filter(WordInSentence.word_id == Word.id).\
        filter(Sentence.id == WordInSentence.sentence_id).\
        group_by(Word.id).\
        limit(100)
    
        response = {"Synsets": [], "Words": []}

        alldocs = len(project.get_documents())

        
        for word in associated_words:
            category = self.get_category(word.pos)
            if category is None:
                continue
            
            row = word._asdict()
            row['category'] = category

            # calculate tf*idf
            tf = word.count
            df = db.session.query(WordCount.document_count).\
                filter(WordCount.word_id == word.id).\
                filter(WordCount.project_id == params["project_id"])[0][0]
            idf = alldocs / df
            row["score_sentences"] = tf * math.log(idf)
            response["Words"].append(row)

        # sort by tf*idf
        response["Words"] = sorted(response["Words"], key=lambda k: k['score_sentences'], reverse=True)

        return jsonify(response)


    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass


register_rest_view(
    AssociatedWordsView,
    wordseer,
    'associated_words_view',
    'associated_word',
    parents=["project"],
)
