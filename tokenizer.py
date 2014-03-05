"""
Set up the tokenizer using the Stanfurd NLP library.
"""

import config
#from corenlp import StanfordCoreNLP
from nltk.tokenize import sent_tokenize

class Tokenizer:
        #def __init__(self):
        #    self.parser = StanfordCoreNLP(config.CORE_NLP_DIR)

        def tokenize_paragraph(par):
            sents = sent_tokenize(par)
            