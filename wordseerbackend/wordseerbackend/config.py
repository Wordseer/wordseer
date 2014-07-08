"""
Configuration file for the pipeline.
"""

import os

WORDSEER_DIR = os.path.dirname(os.path.realpath(__file__))

# NLP locations. Paths should be absolute.
CORE_NLP_DIR = os.path.join(WORDSEER_DIR, "../stanford-corenlp/")

# Processing options
GRAMMATICAL_PROCESSING = True
PART_OF_SPEECH_TAGGING = True
WORD_TO_WORD_SIMILARITY = True
SEQUENCE_INDEXING = True

# Database options
DB_URL = "sqlite:///" + os.path.join(WORDSEER_DIR, 'wordseer.db')
