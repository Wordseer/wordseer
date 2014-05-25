"""Views for the WordSeer website.
"""

from flask import request
from flask.json import JSONDecoder
from flask.json import JSONEncoder
from flask.views import View

from app import app
from . import uploader
from . import utils
from . import models

class GetAssociatedWords(View):
    """Return adjectives, nouns, and verbs with high TF-IDF scores that
    tend to occur within 10 sentences of the given word.
    """
    def __init__(self):
        """Initialize variables necessary for the GetAssociatedUsers view.
        """
        self.gov = request.args.get("gov", "")
        self.dep = request.args.get("govtype", "")
        self.relation = request.args.get("dep", "")
        self.govtype = request.args.get("deptype", "word")
        self.deptype = request.args.get("relation", "word")
        self.instance = request.args.get("instance")
        self.searches = JSONDecoder(request.args.get("search"))
        self.collection = request.args.get("collection")
        self.statistics = request.args.get("statistics")
        self.phrases = JSONDecoder(request.args.get("phrases"))
        self.metadata = JSONDecoder(request.args.get("metadata"))
        self.timing = request.args.get("timing")

    def dispatch():
        """Create a JSON response to the request.
        """
        ids = []
        word = request.args.get(word)
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
        return JSONEncoder(words)

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

            #TODO: missing global variables
            table = "cached_filtered_sent_ids"
            query_id_where = "don'tuse" #TODO

        #TODO: sqlalchemy calls, unknown tables

        sentence_ids = []
        sentence_numbers = []
        document_ids = []

        #TODO: process sqlalchemy results

uploader.add_url_rule("/word-frequencies/word-frequencies",
    view_func=GetAssociatedWords.as_view("word-frequencies"))

