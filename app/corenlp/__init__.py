# corenlp
# Copyright 2013- Hiroyoshi Komatsu
# See LICENSE for details.

"""
Stanford CoreNLP Python wrapper
"""
__version__ = '1.0.3'
__author__ = 'Hiroyoshi Komatsu'
__license__ = 'GNU v2+'

# classes
from corenlp import StanfordCoreNLP, ParserError, TimeoutError, ProcessError
# functions
from corenlp import batch_parse
