"""
Set up the tokenizer using the Stanfurd NLP library.
"""

import config
from corenlp import StanfordCoreNLP
from document import taggedword, sentence
from nltk.tokenize import sent_tokenize


class Tokenizer:
        def __init__(self):
            """Instantiate a tokenizer. This method merely readies the parser.
            Note that readying the parser takes some time.
            """
            
            self.parser = StanfordCoreNLP(config.CORE_NLP_DIR)

        def tokenize(self, txt):
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
                word_list = [] # a list of words
                tagged_words = [] # a list of TaggedWords
                text = s["text"]
                
                for w in s["words"]:
                    if w[0] == ".":
                        tagged_words[-1].space_after = "."
                    word_list.append(w[0])
                    tagged_words.append(taggedword.TaggedWord(
                        word = w, tag = w[1]["PartOfSpeech"]))
                    
                paragraph.append(sentence.Sentence(sentence = text,
                    tagged = tagged_words, words = word_list))

            return paragraph