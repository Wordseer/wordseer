from flask.views import View

class SequenceView(View):
    """Utilities for fetching frequent phrases."""
    
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
