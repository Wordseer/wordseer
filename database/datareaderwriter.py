"""
A stub class used as a placeholder for the actual DataReaderWriter class.
Useful for mocking and for coding.
"""

class DataReaderWriter(object):
    def init_sequence_processing(self):
        pass

    def write_sequences(self):
        pass

    def get_max_sentence_id(self):
        pass

    def record_document_metadata(self):
        pass

    def create_new_document(self, document, number):
        pass

    def calculate_tfidfs(self):
        pass

    def get_document(self, idnum):
        pass

    def get_sentence(self, idnum):
        pass

    def write_parse_products(self, paragraph):
        pass

    def batch_insert(self, sql, csv, suffix):
        pass

    def list_document_ids(self):
        pass

    def load_words(self):
        pass

    def load_sequence_counts(self):
        pass

    def calculate_word_counts(self):
        pass

    def calculate_shared_info(self, position):
        pass

    def calclulate_lin_similarities(self):
        pass

    def index_sequence(self, sequence):
        pass

    def finish_indexing_sequences(self):
        pass

    def get_sentence_ids_for_sequence(self, sequence_id):
        pass

    def write_related_word(self, word, related_word, rel):
        pass

    def finish_grammatical_processing(self):
        pass