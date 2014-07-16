import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers

class GrammaticalSarchView(View):
    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation
    
    
    #=======================================================================
    # endpoint methods
    #=======================================================================
    def get_options(self):
        """php equiv: grammaticalsearch/get-search-options.php"""
        pass
    
    def get_results(self):
        """php equiv: grammaticalsearch/get-search-results.php"""
        pass

    def dispatch_request(self):
        operations = {
            "get_search_options": self.get_search_options,
            "get_search_results": self.get_search_results,
        }

        result = operations[self.operation](self)
        return jsonify(result)

# endpoint urls    
wordseer.add_url_rule("/api/grammaticalsearch/get_options/",
    view_func=GrammaticalSarchView.as_view("gramm_search_get_options", 
                                  "get_search_options"))

wordseer.add_url_rule("/api/grammaticalsearch/get_search_resultss/",
    view_func=GrammaticalSarchView.as_view("gramm_search_get_results", 
                                  "get_search_results"))
