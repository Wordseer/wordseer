import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class SentenceView(View):
    """Utilities and functions for getting a specific set of sentences"""
    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation
        
    #===========================================================================
    # endpoint methods
    #===========================================================================
    
    def get_sentence(self):
        # php equivalent: stripvis/getsentence.php
        pass
    
    def dispatch_request(self):
        operations = {
            "get_sentence": self.get_sentence,
        }

        result = operations[self.operation](self)
        return jsonify(result)

wordseer.add_url_rule("/api/sentences/get_sentence/",
    view_func=SentenceView.as_view("sentence_get", "get_sentence"))
