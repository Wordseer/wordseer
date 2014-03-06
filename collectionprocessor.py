import os
import database
import tokenizer

class CollectionProcessor:
    def process(self, start_from_scratch):
        """
        This function:
        1. Sets up the database if necessary
        2. Extracts metadata, populates the narratives, sentenes, and paragraphs
        tables
        3. Processes the sentences by tokenizing and indexing the words
        4. Processes the sentences by performing grammatical parsing
        Arguments:
        start_from_scratch: If true, then the tables in the database will be
        recreated.
        """   
        # Set up database if necessary
        if start_from_scratch is True:
            with db as database.Database()
                db.reset()
        logger = Logger()

        # TODO: MySQLDataReaderWriter
        
        # TODO: sort out tokenizer
        tokenizer = Tokenizer()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        if not "true" in logger.get("finished_recording_text_and_metadata"):
            
        