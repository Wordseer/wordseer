import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class WordTreeView(View):
    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation
    
    
    #===========================================================================
    # endpoint methods
    #===========================================================================
    
    def get_tree(self):
        """Gets the concordance and grammatical context in which a word tree
    	query occurs."""
        # php equivalent: wordtree/get-tree.php
        pass
    
    def dispatch_request(self):
        operations = {
            "get_tree": self.get_tree,
        }

        result = operations[self.operation](self)
        return jsonify(result)
    
wordseer.add_url_rule("/api/wordtree/get_tree",
    view_func=WordTreeView.as_view("wordtree_get", "get_tree"))
