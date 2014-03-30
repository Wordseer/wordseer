"""
Set up the tokenizer using the Stanford NLP library.
"""

import config
from corenlp import StanfordCoreNLP
from document import taggedword, sentence
from parser.dependency import Dependency
from parser.parseproducts import ParseProducts

#TODO: rename this class something better
class Tokenizer(object):
    """This class takes a string as input and returns a list of Sentences,
    with each word tagged as a TaggedWord."""

    def __init__(self):
        """Instantiate a tokenizer. This method merely readies the parser.
        Note that readying the parser takes some time.
        """

        self.parser = StanfordCoreNLP(config.CORE_NLP_DIR)

    def tokenize(self, txt):
        """Turn a string of one or more sentences into a list of Sentence
        objects.

        :param str txt: One or more sentences, in a string format.
        :return list: A list of document.Sentence objects.
        """

        parsed_text = self.parser.raw_parse(txt)

        return tokenize_from_raw(parsed_text, txt)

    def parse(self, sent, max_length=30):
        """Parse a sentence and extract dependencies, parse trees, etc.

        :param str sent: The sentence as a string.
        :param int max_length: The most amount of words to process.
        """
        parsed = self.parser.raw_parse(sent)
        parsed_sentence = parsed["sentences"][0]
        dependencies = []

        if len(parsed["sentences"]) > 1:
            raise ValueError("More than one sentences"
                " passed in to Parser.parse().")

        for dependency in parsed["sentences"][0]["dependencies"]:
            if dependency[2] > 1 and dependency[4] > 1: #TODO: why?
                gov_index = dependency[2] - 1
                dep_index = dependency[4] - 1
                dependencies.append(Dependency(dependency[0],
                    dependency[1],
                    gov_index,
                    parsed_sentence["words"][gov_index][1]["PartOfSpeech"],
                    dependency[3],
                    parsed_sentence["words"][dep_index][1]["PartOfSpeech"]))

        return ParseProducts(parsed["sentences"][0]["parsetree"],
            dependencies, tokenize_from_raw(sentence, sent)[0].tagged)

def tokenize_from_raw(parsed_text, txt):
    """Given the output of a call to raw_parse, produce tokens.

    :param dict parsed_text: The return value of a call to raw_parse
    :param str txt: The original text.
    :return list: Same output as tokenize().
    """
    paragraph = [] # a list of Sentences

    for s in parsed_text["sentences"]:
        word_list = [] # a list of words
        tagged_words = [] # a list of TaggedWords
        sent_text = s["text"]

        for w in s["words"]:
            tw = taggedword.TaggedWord(word=w, tag=w[1]["PartOfSpeech"],
                lemma=w[1]["Lemma"])

            if txt[int(w[1]["CharacterOffsetBegin"])] != " ":
                tw.space_before = ""

            word_list.append(w[0])
            tagged_words.append(tw)

        paragraph.append(sentence.Sentence(text=sent_text,
            tagged=tagged_words, words=word_list))

    return paragraph
