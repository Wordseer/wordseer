"""
Set up the tokenizer using the Stanfurd NLP library.
"""

import config
from corenlp import StanfordCoreNLP
from document import taggedword, sentence

class Tokenizer(object):
    def __init__(self):
        """Instantiate a tokenizer. This method merely readies the parser.
        Note that readying the parser takes some time.
        """

        self.parser = StanfordCoreNLP(config.CORE_NLP_DIR)

    def tokenize(self, txt):
        """Turn a string of one or more sentences into a list of Sentence
        objects.

        :param str par: One or more sentences, in a string format.
        :return list: A list of document.Sentence objects.
        """

        parsed_text = self.parser.raw_parse(txt)
        paragraph = [] # a list of Sentences

        for s in parsed_text["sentences"]:
            word_list = [] # a list of words
            tagged_words = [] # a list of TaggedWords
            text = s["text"]

            for w in s["words"]:
                tw = taggedword.TaggedWord(word=w, tag=w[1]["PartOfSpeech"],
                    lemma=w[1]["Lemma"])

                if txt[int(w[1]["CharacterOffsetBegin"])] != " ":
                    tw.space_before = ""
                        
                word_list.append(w[0])
                tagged_words.append(tw)

            paragraph.append(sentence.Sentence(sentence=text,
                tagged=tagged_words, words=word_list))

        return paragraph
