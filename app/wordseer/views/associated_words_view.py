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

        sequence_ids = Word.get_matching_sequence_ids(
            params.get("word")[0],
            is_set_id = params.get("class")[0] == "phrase-set")
        sentences = SequenceInSentence.query.filter(
            SequenceInSentence.sequence_id.in_(sequence_ids)).subquery()

        associated_words = db.session.query(
            Word.id.label("id"),
            Word.part_of_speech.label("pos"),
            Word.surface.label("word"),
            func.count(WordInSentence.sentence_id).label("score")).\
        filter(WordInSentence.word_id == Word.id).\
        join(sentences, WordInSentence.sentence_id ==
                        sentences.c.sentence_id).\
        group_by(Word.id).\
        order_by(desc("score"))

        for word in associated_words:
            print word.pos

        associated_sequences = db.session.query(
            Sequence.id.label("sequence_id"),
            Sequence.sequence.label("word"),
            func.count(SequenceInSentence.sentence_id.distinct()).label("score")).\
        filter(SequenceInSentence.sequence_id == Sequence.id).\
        join(sentences, SequenceInSentence.sentence_id ==
                        sentences.c.sentence_id).\
        filter(Sequence.length > 1).\
        filter(Sequence.lemmatized == False).\
        filter(Sequence.all_function_words == False).\
        group_by(Sequence.id).\
        order_by(desc("score"))
        
        response = {"Phrases":[], "Synsets": []}
        for word in associated_words:
            category = self.get_category(word.pos)
            if category is None:
                continue
            if category not in response:
                response[category] = []
            response[category].append(word._asdict())

        for sequence in associated_sequences:
            if sequence.word is None:
                break
            response["Phrases"].append(sequence._asdict())
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
