from datetime import datetime
from document.parsedparagraph import ParsedParagraph
import logger
from .parseproducts import ParseProducts
from sequence.sequenceprocessor import SequenceProcessor

#TODO: documentation

LATEST_SENT_ID = "latest_parsed_sentence_id"
LATEST_SEQ_SENT = "latest_sequence_sentence"

class DocumentParser(object):
    def __init__(self, reader_writer, parser):
        self.reader_writer = reader_writer
        self.parser = parser
        self.sequence_processor = SequenceProcessor()

    def parse_document(self, document):
        """
        :param Document document:
        """

        parse_products = ParseProducts()
        start_time = datetime.now()
        count = 0
        parsed = ParsedParagraph()

        if logger.get(LATEST_SENT_ID) == "":
            current_max = 0
            logger.log(LATEST_SENT_ID, str(current_max), logger.REPLACE)

        else:
            current_max = int(logger.get(LATEST_SENT_ID))

        for sentence in document.sentences:
            if sentence.id > int(logger.get(LATEST_SENT_ID)):
                parse_products = parser.parse(sentence.sentence)
                parsed.add_sentence(sentence, parse_products)
                count += 1
                current_max = sentence.id

                if count % 50 == 0:
                    average_time = (datetime.now - start_time).total_seconds()
                    print("Average parse speed after " + count +
                        " sentences: " + str(average_time / count) +
                        " seconds per sentence")

                    #TODO: reader_writer
                    #self.write_and_parse(parsed, current_max)

                    parsed = ParsedParagraph()

        #TODO: reader_writer
        #self.write_and_parse(parsed, current_max)

    def write_and_parse(self, products, current_max):
        """Send a ParseProducts object to the ReaderWriter for writing, then
        process each sentence returned from the ReaderWriter with
        SequenceProcessor, then call write_sequences on reader_writer.

        :param ParseProducts products: The ParseProducts to send
        :param int current_max: The highest sentence ID yet processed, used for
        logging purposes
        """

        sentences = self.reader_writer.write_parse_products(products)

        logger.log(LATEST_SENT_ID, str(current_max), logger.REPLACE)
        for sentence in sentences:
            self.sequence_processor.process(sentence)

        logger.log(LATEST_SEQ_SENT, str(current_max), logger.REPLACE)
        self.reader_writer.write_sequences()
