import os
from nltk.tokenize import sent_tokenize

import config
import database

class CollectionProcessor:
    # Todo: Figure out config stuff
    def process(self):
        """
        Get parameters
        """
        
        # Set up database
        db = database.Database(config.db_url)
        print db

a = CollectionProcessor()
a.process()
        