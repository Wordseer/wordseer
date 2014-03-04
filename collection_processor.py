import os
import config
import database
import tokenizer

class CollectionProcessor:
    def process(self):        
        # Set up database
        db = database.Database(config.db_url)
        print db

        # TODO: sort out tokenizer
        tokenizer = Tokenizer()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        

a = CollectionProcessor()
a.process()
        