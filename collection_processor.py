import os
from sqlalchemy import create_engine
from nltk.tokenize import sent_tokenize
from corenlp import StanfordCoreNLP
import config

class CollectionProcessor {
    # Todo: Figure out config stuff
    def process(self):
        """
        Get parameters
        """
        
        # Set up database
        engine = create_engine(config.db_url)
        
        
    