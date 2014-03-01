CORE_NLP_DIR = "stanford-corenlp-dir/"
PARSER = StanfordCoreNLP(CORE_NLP_DIR)

grammatical_processing = True; 
part_of_speech_tagging = True;
word_to_word_similarity = True;
sequence_indexing = True;

db = {
    "server": "localhost:3306",
    "name": "",}