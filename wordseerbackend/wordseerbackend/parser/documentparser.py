"""
The DocumentParser takes in a Document object and parses it by creating a
ParsedParagraph object for every sentence in the Document.

The ParsedParagraph will then be written to the database, and each sentence
returned from the write_parse_products method will be passed to
SequenceProcessor.process().
"""

from datetime import datetime

from ..document.parsedparagraph import ParsedParagraph
from .. import logger
from ..parser.parseproducts import ParseProducts
from ..sequence.sequenceprocessor import SequenceProcessor

LATEST_SENT_ID = "latest_parsed_sentence_id"
LATEST_SEQ_SENT = "latest_sequence_sentence"

class DocumentParser(object):
    """Handle parsing a document.
    """
    def __init__(self, reader_writer, parser):
        self.reader_writer = reader_writer
        self.parser = parser
        self.sequence_processor = SequenceProcessor(reader_writer)

    def parse_document(self, document):
        """ Parse a document and write it to the database.

        Given a certain document, this method will parse every sentence in
        it to a ParsedParagraph object. Ater every 50th sentence it will call
        write_and_parse and supply the ParseProducts and the latest sentence ID.

        :param Document document: The document to parse and record.
        """

        start_time = datetime.now()
        count = 0
        parsed = ParsedParagraph()

        try:
            current_max = int(logger.get(LATEST_SENT_ID))
        except ValueError:
            current_max = 0
            logger.log(LATEST_SENT_ID, str(current_max), logger.REPLACE)

        #TODO: both of the below comments should replace the lines below
        # them once the pipeline is integrated with the main application
        #for sentence in document.all_sentences:
        for sentence in document.sentences:
            if sentence.id > int(logger.get(LATEST_SENT_ID)):
                #parse_products = self.parser.parse(sentence.text)
                parse_products = self.parser.parse(sentence.sentence)
                parsed.add_sentence(sentence, parse_products)
                count += 1
                current_max = sentence.id

                if count % 50 == 0:
                    average_time = (datetime.now() - start_time).total_seconds()
                    print("Average parse speed after " + str(count) +
                        " sentences: " + str(average_time / count) +
                        " seconds per sentence")

                    self.write_and_parse(parsed, current_max)

                    parsed = ParsedParagraph()
        self.write_and_parse(parsed, current_max)

    def write_and_parse(self, products, current_max):
        """Send a ParsedParagraph object to the ReaderWriter for writing, then
        process each sentence returned from the write_parse_products with
        SequenceProcessor.process(), then call ReaderWriter.write_sequences().
        This method also updates the logs with the latest sentence ID and latest
        sequenced sentence.

        :param ParsedParagraph products: The ParsedParagraph to send
        :param int current_max: The highest sentence ID yet processed.
        """
        #TODO: reader_writer
        sentences = self.reader_writer.write_parse_products(products)

        logger.log(LATEST_SENT_ID, str(current_max), logger.REPLACE)

        for sentence in sentences:
            self.sequence_processor.process(sentence)

        logger.log(LATEST_SEQ_SENT, str(current_max), logger.REPLACE)
        #TODO: reader_writer
        self.reader_writer.write_sequences()

