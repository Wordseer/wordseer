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
                result = {
                    "sentence": self.make_sentence_dict(sentence,
                                                        matching_words),
                    "id": sentence.id,
                    "document_id": sentence.document_id,
                    "sentence_set": " ".join([str(set.id) for set in sentence.sets])                 
                }
                self.add_metadata_properties(sentence, result)
                results.append(result)
            return jsonify(results = results, total = len(results))

    def make_sentence_html(self, sentence, matching_words):
        """ Constructs an HTML string to display to the user, in which each
        word is enclosed by a <span class='word' word-id=<word_id>
        sentence-id=<sentence_id>></span> and the whole
        sentence is enclosed by a <span class='sentence'>. We sould send the
        raw data, and have the javascript create and render the HTML, but
        creating the HTML server side turns out to be much faster in practice.
        """
        html = ["<span class='sentence'>"]
        for word_in_sentence in sentence.word_in_sentence:
            html_classes = ["word"]
            if word_in_sentence.word.id in matching_words:
                html_classes.append("search-highlight")
            word_html = "".join([
                word_in_sentence.space_before, 
                "<span ",
                " word-id='", str(word_in_sentence.word.id),  "' ",
                " position='", str(word_in_sentence.position), "' ",
                " sentence-id='", str(sentence.id), "' ",
                "class='"," ".join(html_classes), "'>",
                word_in_sentence.surface,
                "</span>"])
            html.append(word_html)
        html.append("</span>")
        return "".join(html)

    def add_metadata_properties(self, sentence, result):
        """Adds the properties of each sentence to the dictionary being sent to
        the client."""
        for property in sentence.properties:
            result[property.name] = property.value

    def make_sentence_dict(self, sentence, matching_words):
        sentence_dict = {}
        sentence_dict["words"] = self.make_sentence_html(sentence,
                                                         matching_words)
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
