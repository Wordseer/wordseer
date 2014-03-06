"""
Set up the tokenizer using the Stanfurd NLP library.
"""

import config
from corenlp import StanfordCoreNLP
from document import TaggedWord, Sentence
from nltk.tokenize import sent_tokenize

class Tokenizer:
        def __init__(self):
            """Instantiate a tokenizer. This method merely readies the parser.
            Note that readying the parser takes some time.
            """
            
            self.parser = StanfordCoreNLP(config.CORE_NLP_DIR)

        def tokenize(txt):
            """Turn a string of one or more sentences into a list of Sentence
            objects.

            Args:
                par (str): One or more sentences, in a string format.

            Returns:
                A list of document.Sentence objects.
            """

            parsed_text = self.parser.raw_parse(txt)
            paragraph = [] # a list of Sentences
            
            for s in parsed_text["sentences"]:
                words = [] # a list of words
                tagged = [] # a list of TaggedWords
                text = sentence["text"]
                
                for w in sentence["words"]:
                    if w[0] == ".":
                        words[-1].space_after = "."
                    words.append(w)
                    tagged.append(TaggedWord(word = w, tag = w["PartOfSpeech"]))
                    
                paragraph.append(Sentence(sentence = text,
                    tagged = tagged, words = words)))

            return paragraph