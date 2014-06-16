"""Get words associated with a given word.
"""

import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers
from ..models import CachedSentences
from ...uploader.models import WordInSentence

class GetAssociatedWords(View):
    """Return adjectives, nouns, and verbs with high TF-IDF scores that
    tend to occur within 10 sentences of the given word.

    The expected url arguments are documented below.

    Keyword Arguments:
        phrases (str):
        govtype (str):
        dep (str):
        deptype (str):
        relation (str):
        phrases (JSON): Required.
        metadata (JSON): Required.
        searches (JSON): Required.
        collection (str): Required.
        statistics (str): Required.
        timing (str): Required.
        instance (str): Required.
    """
    def __init__(self):
        """Initialize variables necessary for the GetAssociatedUsers view.
        """
        self.gov = request.args.get("gov", "")
        self.dep = request.args.get("govtype", "")
        self.relation = request.args.get("dep", "")
        self.govtype = request.args.get("deptype", "word")
        self.deptype = request.args.get("relation", "word")

        try:
            self.phrases = json.loads(str(request.args["phrases"]))
            self.metadata = json.loads(str(request.args["metadata"]))
            self.searches = json.loads(str(request.args["search"]))
            self.collection = request.args["collection"]
            self.statistics = request.args["statistics"]
            self.timing = request.args["timing"]
            self.instance = request.args["instance"]
        except ValueError:
            abort(400)

    def dispatch_request(self):
        """Create a JSON response to the request.
        """
        ids = []
        word = request.args.get("word")
        if request.args.get("id"):
            id_number = request.args.get("id")
            ids = id_number
        elif request.args.get("word"):
            cls = request.args.get("class")
            if cls == "phrase-set":
                ids = utils.get_word_ids_from_phrase_set(word)
            elif cls == "word":
                ids = utils.get_word_ids(word)
            elif cls == "phrase":
                ids = word.split()

        words = self.get_associated_words(ids, word)
        return jsonify(words)

    def get_associated_words(self, ids, word):
        """Find the relevant adjectives, nouns, and verbs.

        Args:
            ids (list of ints): A list of word IDs to find associated words for.
            word (str): The word itself.

        Returns:
            list of
        """
        ids = ", ".join(ids)
        context_conditions = ""
        table_id = ""
        query_id_where = ""

        if request.args.get("query_id"):
            table = "filtered_sent_ids"

            table = "cached_filtered_sent_ids"
            query_id_where = "don'tuse" #TODO

            words = db.session.query(CachedSentences).join(word_in_sentence)
        sentence_ids = []
        sentence_numbers = []
        document_ids = []

        #TODO: process sqlalchemy results

wordseer.add_url_rule("/word-frequencies/word-frequencies",
    view_func=GetAssociatedWords.as_view("word-frequencies"))

