"""Methods to handle string parsing, tokenization, tagging, etc.
"""

from corenlp import StanfordCoreNLP

from app import app
from app.models.sentence import Sentence
from app.models.word import Word
from app.models.parseproducts import ParseProducts

class StringProcessor(object):
    """Tokenize or parse a string.
    """

    def __init__(self):
        """Instantiate and ready the parser. Note that readying the parser takes
        some time.
        """

        self.parser = StanfordCoreNLP(app.config["CORE_NLP_DIR"])

    def tokenize(self, txt):
        """Turn a string of one or more ``Sentence``\s into a list of
        ``Sentence`` objects. This method will also tokenize each word in txt,
        find its PoS, lemma, and space_before.

        :param str txt: One or more sentences, in a string format.
        :return list: A list of document.Sentence objects.
        """
        parsed_text = self.parser.raw_parse(txt)

        return tokenize_from_raw(parsed_text, txt)

    def parse(self, sent, max_length=30):
        """Parse a ``Sentence`` and extract dependencies, parse trees, etc.

        Note that for max_length, a "word" is defined as something with a space
        on at least one side. This is not the typical definition of "word".
        This is done so that length can be checked before resources are
        committed to processing a very long sentence.

        :param str sent: The ``Sentence`` as a string.
        :param int max_length: The most amount of words to process.
        """

        # This isn't a perfect way to check how many words are in a sentence,
        # but it's not so bad.
        if len(sent.split(" ")) > max_length:
            raise ValueError("Sentence appears to be too long, max length " +
                "is " + str(max_length))

        parsed = self.parser.raw_parse(sent)
        parsed_sentence = parsed["sentences"][0]
        dependencies = []

        if len(parsed["sentences"]) > 1:
            raise ValueError("More than one sentences passed in to"
                " StringProcessor.parse().")

        for dependency in parsed_sentence["dependencies"]:
            # We don't want to make a dependency involving ROOT
            if int(dependency[2]) > 0 and int(dependency[4]) > 0:
                gov_index = int(dependency[2]) - 1
                dep_index = int(dependency[4]) - 1
                governor_pos = parsed_sentence["words"][gov_index][1]\
                    ["PartOfSpeech"]

                dependent_pos = parsed_sentence["words"][dep_index][1]\
                    ["PartOfSpeech"]

                dependencies.append({
                    "grammatical_relationship": dependency[0],
                    "governor": dependency[1],
                    "governor_index": gov_index,
                    "governor_pos": governor_pos,
                    "dependent": dependency[3],
                    "dependent_index": dep_index,
                    "dependent_pos": dependent_pos})

        return ParseProducts(parsed["sentences"][0]["parsetree"],
            dependencies, tokenize_from_raw(parsed, sent)[0].tagged)

def tokenize_from_raw(parsed_text, txt):
    """Given the output of a call to raw_parse, produce a list of Sentences
    and find the PoS, lemmas, and space_befores of each word in each sentence.

    This method does the same thing as tokenize(), but it accepts already parsed
    data.

    :param dict parsed_text: The return value of a call to raw_parse
    :param str txt: The original text.
    :return list: A list of document.Sentence objects.
    """
    paragraph = [] # a list of Sentences

    for sentence in parsed_text["sentences"]:
        word_list = [] # a list of words
        tagged_words = [] # a list of Words
        sentence_text = sentence["text"]

        for word in sentence["words"]:
            #FIXME not quite right
            word_object = Word(word=word[0],
                part_of_speech=word[1]["PartOfSpeech"],
                lemma=word[1]["Lemma"])

            if txt[int(word[1]["CharacterOffsetBegin"])] != " ":
                word_object.space_before = ""

            word_list.append(word[0])
            tagged_words.append(word_object)

        paragraph.append(Sentence(text=sentence_text,
            words=tagged_words))

    return paragraph

