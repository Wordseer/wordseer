import os

from nltk.tokenize import sent_tokenize
from corenlp import StanfordCoreNLP
import config
import database

class CollectionProcessor {
    # Todo: Figure out config stuff
    def process(self):
        """
        Get parameters
        """
        
        # Set up database
        engine = create_engine(config.db_url)
        
        
    