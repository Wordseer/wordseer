"""Methods to handle string parsing, tokenization, tagging, etc.
"""

from corenlp import StanfordCoreNLP

from . import config
from app.models.sentence import Sentence
from app.models.word import Word
from app.models.parseproducts import ParseProducts
from app import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

class StringProcessor(object):
    """Tokenize or parse a string.
    """

    def __init__(self):
        """Instantiate and ready the parser. Note that readying the parser takes
        some time.
        """

        self.parser = StanfordCoreNLP(config.CORE_NLP_DIR)

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
        if len(sent.text.split(" ")) > max_length:
            raise ValueError("Sentence appears to be too long, max length " +
                "is " + str(max_length))

        parsed = self.parser.raw_parse(sent.text)
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
                governor_lemma = parsed_sentence["words"][gov_index][1]\
                    ["Lemma"]

                dependent_pos = parsed_sentence["words"][dep_index][1]\
                    ["PartOfSpeech"]
                dependent_lemma = parsed_sentence["words"][dep_index][1]\
                    ["Lemma"]

                dependencies.append({
                    "grammatical_relationship": dependency[0],
                    "governor": dependency[1],
                    "governor_index": gov_index,
                    "governor_pos": governor_pos,
                    "governor_lemma": governor_lemma,
                    "dependent": dependency[3],
                    "dependent_index": dep_index,
                    "dependent_pos": dependent_pos,
                    "dependent_lemma": dependent_lemma,
                    "sentence_id": sent.id,
                })

        parse_product = { "dependencies": dependencies } # add other keys as needed
        # return ParseProducts(parsed["sentences"][0]["parsetree"],
        #     dependencies, tokenize_from_raw(parsed, sent)[0].tagged)
        return parse_product

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
    words = dict()

    for sentence_data in parsed_text["sentences"]:
        sentence = Sentence(text = sentence_data["text"])

        position = 0
        for word_data in sentence_data["words"]:

            word = word_data[0]
            tag = word_data[1]["PartOfSpeech"]
            lemma = word_data[1]["Lemma"]

            key = (word, tag, lemma)

            # TODO: proper space_before implementation

            if key in words.keys():
                word = words[key]
                # print("In dict " + str(word))
            else:

                try:
                    word = Word.query.filter_by(
                        word = word,
                        lemma = lemma,
                        tag = tag
                    ).one()
                    # print("Found word " + str(word))
                except(MultipleResultsFound):
                    print("ERROR: duplicate records found for:")
                    print("\t" + str(key))
                except(NoResultFound):
                    word = Word(
                        word = word,
                        lemma = lemma,
                        tag = tag
                    )
                    # print("New word " + str(word))
                    
                words[key] = word

            sentence.add_word(
                word = word,
                position = position,
                space_before = "", # word["space_before"],
                tag = word.tag
            )

            position += 1

        paragraph.append(sentence)

    db.session.commit()
    return paragraph

