"""
Configuration file for the pipeline.
"""

# NLP locations
CORE_NLP_DIR = "stanford-corenlp/"

# Processing options
GRAMMATICAL_PROCESSING = True
PART_OF_SPEECH_TAGGING = True
WORD_TO_WORD_SIMILARITY = True
SEQUENCE_INDEXING = True

# Database options
DB_URL = 'sqlite:///wordseer.db'
