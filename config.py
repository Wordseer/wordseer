"""
Configuration file for the pipeline.
"""
from corenlp import StanfordCoreNLP


CORE_NLP_DIR = "stanford-corenlp/"
PARSER = StanfordCoreNLP(CORE_NLP_DIR)

grammatical_processing = True; 
part_of_speech_tagging = True;
word_to_word_similarity = True;
sequence_indexing = True;

db_url = 'sqlite:///wordseer.db'