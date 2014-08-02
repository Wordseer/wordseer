"""The DocumentParser takes in a Document object and parses it by creating a
ParsedParagraph object for every sentence in the Document.

The ParsedParagraph will then be written to the database, and each sentence
returned from the write_parse_products method will be passed to
SequenceProcessor.process().
"""
from datetime import datetime
import logging

from app.models.parsedparagraph import ParsedParagraph
from . import logger
from app.models.parseproducts import ParseProducts
from .sequenceprocessor import SequenceProcessor
from app import db

LATEST_SENT_ID = "latest_parsed_sentence_id"
LATEST_SEQ_SENT = "latest_sequence_sentence"

class DocumentParser(object):
    """Handle parsing a document.
    """
    def __init__(self, reader_writer, parser, project):
        self.pylogger = logging.getLogger(__name__)
        self.reader_writer = reader_writer
        self.parser = parser
        self.sequence_processor = SequenceProcessor(reader_writer)
        self.project = project

    def parse_document(self, document):
        """Parse a document and write it to the database.

        Given a certain document, this method will parse every sentence in
        it to a ParsedParagraph object. Ater every 50th sentence it will call
        write_and_parse and supply the ParseProducts and the latest sentence ID.

        :param Document document: The document to parse and record.
        """
        pdb.set_trace()

        start_time = datetime.now()
        count = 0
        products = []

        try:
            current_max = int(logger.get(self.project, LATEST_SENT_ID))
        except ValueError:
            current_max = 0
            logger.log(self.project, LATEST_SENT_ID, str(current_max),
                logger.REPLACE)

        relationships = dict()
        dependencies = dict()
        sentence_count = len(document.all_sentences)
        for sentence in document.all_sentences:
            if sentence.id > int(logger.get(self.project, LATEST_SENT_ID)):
                parsed = self.parser.parse(sentence, relationships,
                    dependencies)
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

