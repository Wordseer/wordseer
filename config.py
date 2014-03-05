"""
Configuration file for the pipeline.
"""

# NLP locations
CORE_NLP_DIR = "stanford-corenlp/"

# Processing options
grammatical_processing = True; 
part_of_speech_tagging = True;
word_to_word_similarity = True;
sequence_indexing = True;

# Database options
db_url = 'sqlite:///wordseer.db'
