from flask.views import MethodView
from flask.json import jsonify, dumps, loads
from flask import request
from nltk import word_tokenize

from app import app
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view
from app.wordseer.helpers import parse_phrase_strings

class SentencesView(MethodView):
    """Returns data that backs the Sentence List view for a set of results."""

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)        
        query = Query.query.get(params["query_id"])
        # Determine the words, phrases or phrase sets that match the query in
        # order to send back information about which terms should be highlighted
        # in the UI.
        matching_words = self.get_matching_words(params)
        if query:
            # If we're being asked for a single sentence view, then just return
            # the data for that sentence.
            sentence = Sentence.query.get(params["sentence_id"]);
            if sentence is not None:
                return jsonify(
                    self.make_single_sentence_view(sentence,
                                                   matching_words))
            # If not, then return the data for all the sentences that match the
            # query.
            results = []
            total = len(query.sentences)
            start = int(params["start"][0])

            end = int(params["limit"][0]) + start

            for sentence in query.sentences[start:end]:
                result = {
                    "sentence": self.make_sentence_dict(sentence,
                                                        matching_words),
                    "id": sentence.id,
                    "document_id": sentence.document_id,
                    "sentence_set": " ".join([str(set.id) for set in sentence.sets])                 
                }
                self.add_metadata_properties(sentence, result)
                results.append(result)
            return jsonify(results = results, total = total)

    def get_matching_words(self, params):
        matching_words = []
        if "gov" in params and "govtype" in params and params["gov"][0]:
            is_set_id = params["govtype"][0] != "word"
            search_lemmas = "all_word_forms" in params and params["all_word_forms"][0] == 'on'
            matching_words.extend(Word.get_matching_word_ids(params["gov"][0],
                is_set_id, search_lemmas))
        if "dep" in params and "deptype" in params and params["dep"][0]:
            is_set_id = params["deptype"][0] != "word"
            search_lemmas = "all_word_forms" in params and params["all_word_forms"][0] == 'on'
            matching_words.extend(Word.get_matching_word_ids(params["dep"][0],
                is_set_id, search_lemmas))
        return matching_words

    def make_single_sentence_view(self, sentence, matching_words):
        result = {}
        result["sentence"] = sentence.text
        result["sentence_id"] = sentence.id
        result["document_id"] = sentence.document_id
        result["govIndex"] = []
        metadata = {}
        for property in sentence.properties:
            if property.name not in metadata:
                metadata[property.name] = {"children": []}
            metadata[property.name]["children"].append(
                {"propertyName": property.name,
                 "text": property.value})
        result["metadata"] = metadata
        words = []
        for i, word in enumerate(sentence.word_in_sentence):
            word_info = {
                "word": word.surface,
                "word_id": word.word_id,
                "space_before": word.space_before
            }
            if word.word.id in matching_words:
                result["govIndex"].append(i)
            words.append(word_info)
        result["words"] = words
        return result


    def make_sentence_html(self, sentence, matching_words):
        """ Constructs an HTML string to display to the user, in which each
        word is enclosed by a <span class='word' word-id=<word_id>
        sentence-id=<sentence_id>></span> and the whole
        sentence is enclosed by a <span class='sentence'>. We could send the
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
        sentence_dict["words"] = self.make_sentence_html(sentence, matching_words)
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
