from sequence.sequenceprocessor import SequenceProcessor
#TODO: documentation
class DocumentParser(object):
    def __init__(self, reader_writer, parser):
        self.reader_writer = reader_writer
        self.parser = parser
        self.sequence_processor = SequenceProcessor()

    def parse_document(document):
        """
        :param Document document:
        """

        parse_products = ParseProducts()