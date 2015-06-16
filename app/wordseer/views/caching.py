from flask.json import jsonify 

from flask.views import View

from app.wordseer import wordseer

# TODO: do we even need this anymore? 
class CachingView(View):
    """Utilities for caching the the sentences, phrases, and documents
    that match a query.
    """
#     php equivalent: caching/caching.php
    
    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation
        
    #===========================================================================
    # helper functions
    #===========================================================================
    
    def make_cache_tables(self):
        """Creates tables to cache the results of applying the filters
        for this query."""
        pass

    def get_next_query_id(self):
        pass

    #=======================================================================
    # endpoint functions
    #=======================================================================
    
    def dispatch_clear_query_cache(self, query_id):
        pass

    def dispatch_caching(self, searches, collection, metadata, phrases):
        """Does the filtering operations necessary for the query and
        prints out a new query ID."""
        pass

    
    def dispatch_request(self):
            operations = {
                "dispatch_clear_query_cache": self.dispatch_clear_query_cache,
                "dispatch_caching": self.dispatch_caching,
            }
    
            result = operations[self.operation](self)
            return jsonify(result)
  
      
wordseer.add_url_rule("/api/caching/dispatch_clear/",
    view_func=CachingView.as_view("caching_dispatch_clear", 
                                  "dispatch_clear_query_cache"))

wordseer.add_url_rule("/api/caching/dispatch/",
    view_func=CachingView.as_view("caching_dispatch", "dispatch_caching"))

