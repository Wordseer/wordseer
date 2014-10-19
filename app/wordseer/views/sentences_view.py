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
        query = Query.query.get(params["query_id"])
        matching_words = []
        if "gov" in params and "govtype" in params:
            is_set_id = params["govtype"][0] != "word"
            matching_words.extend(Word.get_matching_word_ids(params["gov"][0],
                is_set_id))
        if "dep" in params and "deptype" in params:
            is_set_id = params["deptype"][0] != "word"
            matching_words.extend(Word.get_matching_word_ids(params["dep"][0],
                is_set_id))
        if query:
            results = []
            for sentence in query.sentences:
                results.append({
                    "sentence": self.make_sentence_dict(sentence,
                                                        matching_words),
                    "id": sentence.id,
                    "document_id": sentence.document_id,
                    "sentence_set": " ".join(sentence.sets)                 
                })
            return jsonify(results = results, total = len(results))

    def make_sentence_dict(self, sentence, matching_words):
        # TODO: add search params to make highlighting easier.
        sentence_dict = {}
        html = []
        for word in sentence.word_in_sentence:
            html_classes = ["word"]
            if word.word.id in matching_words:
                html_classes.append("search-highlight")
            word_html = "".join(["<span ", "class='", " ".join(html_classes), "'>",
                word.space_before, word.surface, "</span>"])
            html.append(word_html)
        sentence_dict["words"] = "".join(html)
        return sentence_dict

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
