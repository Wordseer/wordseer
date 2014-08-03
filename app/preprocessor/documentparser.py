"""The DocumentParser takes in a Document object and parses it by sending
every sentence to the `StringProcessor`, which writes it to the database.
"""

from datetime import datetime
import logging

from . import logger
from .sequenceprocessor import SequenceProcessor
from app import db

LATEST_SENT_ID = "latest_parsed_sentence_id"
LATEST_SEQ_SENT = "latest_sequence_sentence"

class DocumentParser(object):
    """Handle parsing a document.
    """
    def __init__(self, parser):
        self.pylogger = logging.getLogger(__name__)
        self.parser = parser
        self.sequence_processor = SequenceProcessor()

    def parse_document(self, document):
        """Parse a document and write it to the database.

        Given a certain document, this method will parse every sentence in
        it. Ater every 50th sentence it will call write_and_parse and supply the
        ParseProducts and the latest sentence ID.

        :param Document document: The document to parse and record.
        """

        start_time = datetime.now()
        count = 0
        products = []

        try:
            current_max = int(logger.get(LATEST_SENT_ID))
        except ValueError:
            current_max = 0
            logger.log(LATEST_SENT_ID, str(current_max), logger.REPLACE)

        relationships = dict()
        dependencies = dict()
        sequences = dict()
        sentence_count = len(document.all_sentences)
        for sentence in document.all_sentences:
            if sentence.id > int(logger.get(LATEST_SENT_ID)):
                parsed = self.parser.parse(sentence, relationships, dependencies)
                self.sequence_processor.process(sentence, sequences)
                products.append(parsed)
                count += 1
                current_max = sentence.id

                if count % 50 == 0 or count == sentence_count:
                    average_time = (datetime.now() - start_time).total_seconds()
                    self.pylogger.info("Average parse speed after %s sentences:"
                        " %s seconds per sentence", str(count),
                        str(average_time / count))

                    products = []
                    relationships = dict()
                    dependencies = dict()
                    
                    db.session.commit()
        db.session.commit()

