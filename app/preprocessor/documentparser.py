"""The DocumentParser takes in a Document object and parses it by sending
every sentence to the `StringProcessor`, which writes it to the database.
"""
import pdb
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
    def __init__(self, str_proc, project):
        self.logger = logging.getLogger(__name__)
        self.string_processor = str_proc
        self.sequence_processor = SequenceProcessor(project)
        self.project = project
        self.project_logger = logger.ProjectLogger(self.logger, self.project)

    def parse_document(self, document):
        """Parse a document and write it to the database.

        Given a certain document, this method will parse every sentence in
        it. Ater every 50th sentence it will call write_and_parse and supply the
        ParseProducts and the latest sentence ID.

        :param Document document: The document to parse and record.
        """
        #pdb.set_trace()

        start_time = datetime.now()
        count = 0
        products = []
        current_max = 0

        try:
            current_max = int(logger.get(self.project, LATEST_SENT_ID))
        except ValueError:
            current_max = 0
            logger.log(self.project, LATEST_SENT_ID, str(current_max),
                logger.REPLACE)

        relationships = dict()
        dependencies = dict()
        sequences = dict()
        sentence_count = len(document.all_sentences)
        for sentence in document.all_sentences:
            if sentence.id > current_max:
                
                self.string_processor.parse(sentence, relationships,
                    dependencies)
                
                self.sequence_processor.process(sentence, sequences)
                
                count += 1
                current_max = sentence.id

                if count % 50 == 0 or count == sentence_count:
                    average_time = (datetime.now() - start_time).total_seconds()
                    self.project_logger.info("Average parse speed after %s "
                        "sentences: %s seconds per sentence", str(count),
                        str(average_time / count))
                    relationships = dict()
                    dependencies = dict()
                    sequences = dict()

                    db.session.commit()

        db.session.commit()
