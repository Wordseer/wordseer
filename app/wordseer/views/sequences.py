from flask.json import jsonify

from flask.views import View
from app.wordseer import wordseer

class SequenceView(View):
    """Utilities for fetching frequent phrases."""
    # php equivalent: phrases/get-phrases.php
    
    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation
        
    #===========================================================================
    # helper methods
    #===========================================================================
    
    @staticmethod
    def get_sequence_ids(seq_str):
        """takes a string from client in the following format: 
        "('word' or 'phrase')_(id)"
        and parses it to return the corresponding sequence object
        """
        components = seq_str.split("_")
        seq_type = components[0]
        seq_id = int(components[1])
        if type == "phrase":
            return seq_id
        # TODO: deal with what happens when type == "word"
        
    #===========================================================================
    # endpoint methods
    #===========================================================================
    
    def get_sequences_in_sentence(self):
        pass
    
    def get_sequences(self):
        pass
    
    def dispatch_request(self):
        operations = {
            "get_sequences_in_sentence": self.get_sequences_in_sentence,
            "get_sequences": self.get_sequences,
        }

        result = operations[self.operation](self)
        return jsonify(result)
    
# endpoint urls
wordseer.add_url_rule("/api/sequences/get_sequences/",
    view_func=SequenceView.as_view("seq_get_sequences", "get_sequences"))

wordseer.add_url_rule("/api/sequences/get_sequences_in_sentence/",
    view_func=SequenceView.as_view("seq_get_sequences_in_sentence",
                                   "get_sequences_in_sentence"))
