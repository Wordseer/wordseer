class Sequence(object):
    def __init__(self, *args, **kwargs):
        """
        	:keyword str sequence_id:
            :keyword int start_position:
            :keyword int sentence_id:
            :keyword int document_id:
            :keyword str sequence:
            :keyword boolean is_lemmatized:
            :keyword boolean has_function_words:
            :keyword boolean all_function_words:
            :keyword int length:
            :keyword list words:
        """
        for item, value in kwargs:
            setattr(self, item, value)