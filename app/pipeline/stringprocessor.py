"""Methods to handle string parsing, tokenization, tagging, etc.
"""
from corenlp import StanfordCoreNLP

from app import app
from app.models.sentence import Sentence
from app.models.word import Word
from app.models.dependency import Dependency
from app.models.grammaticalrelationship import GrammaticalRelationship
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

    def parse(self, sentence, relationships=None, dependencies=None, max_length=30):
        """Parse a ``Sentence`` and extract dependencies, parse trees, etc.

        Note that for max_length, a "word" is defined as something with a space
        on at least one side. This is not the typical definition of "word".
        This is done so that length can be checked before resources are
        committed to processing a very long sentence.

        :param Sentence sentence: The ``Sentence`` object.
        :param int max_length: The most amount of words to process.
        """

        # This isn't a perfect way to check how many words are in a sentence,
        # but it's not so bad.
        #if len(sentence.text.split(" ")) > max_length:
        #   raise ValueError("Sentence appears to be too long, max length " +
        #        "is " + str(max_length))
        # TODO: figure out the above
        parsed = self.parser.raw_parse(sentence.text)
        parsed_sentence = parsed["sentences"][0]

        if len(parsed["sentences"]) > 1:
            raise ValueError("More than one sentences passed in to"
                " StringProcessor.parse().")

        for dependency in parsed_sentence["dependencies"]:
            # We don't want to make a dependency involving ROOT
            if int(dependency[2]) > 0 and int(dependency[4]) > 0:
                governor = dependency[1]
                dependent = dependency[3]
                governor_index = int(dependency[2]) - 1
                dependent_index = int(dependency[4]) - 1
                governor_pos = parsed_sentence["words"][governor_index][1]\
                    ["PartOfSpeech"]
                governor_lemma = parsed_sentence["words"][governor_index][1]\
                    ["Lemma"]
                dependent_pos = parsed_sentence["words"][dependent_index][1]\
                    ["PartOfSpeech"]
                dependent_lemma = parsed_sentence["words"][dependent_index][1]\
                    ["Lemma"]
                grammatical_relationship = dependency[0]

                # If dictionaries are present, run with duplication handling
                if relationships != None and dependencies != None:
                    key = grammatical_relationship

                    if key in relationships.keys():
                        relationship = relationships[key]
                    else:

                        try:
                            relationship = GrammaticalRelationship.query.filter_by(
                                name = grammatical_relationship
                            ).one()
                        except(MultipleResultsFound):
                            print("ERROR: duplicate records found for:")
                            print("\t" + str(key))
                        except(NoResultFound):
                            relationship = GrammaticalRelationship(
                                name = grammatical_relationship
                            )

                        relationships[key] = relationship

                    # Read the data for the governor, and find the corresponding word
                    governor = Word.query.filter_by(
                        word = governor,
                        lemma = governor_lemma,
                        part_of_speech = governor_pos
                    ).first()

                    # Same as above for the dependent in the relationship
                    dependent = Word.query.filter_by(
                        word = dependent,
                        lemma = dependent_lemma,
                        part_of_speech = dependent_pos
                    ).first()

                    key = (relationship.name, governor.id, dependent.id)

                    if key in dependencies.keys():
                        dependency = dependencies[key]
                    else:

                        try:
                            dependency = Dependency.query.filter_by(
                                grammatical_relationship = relationship,
                                governor = governor,
                                dependent = dependent
                            ).one()
                        except(MultipleResultsFound):
                            print("ERROR: duplicate records found for:")
                            print("\t" + str(key))
                        except(NoResultFound):
                            dependency = Dependency(
                                grammatical_relationship = relationship,
                                governor = governor,
                                dependent = dependent
                            )

                        dependencies[key] = dependency

                    # Add the dependency to the sentence
                    sentence.add_dependency(
                        dependency = dependency,
                        governor_index = governor_index,
                        dependent_index = dependent_index,
                    )

                    #  print("relationship", relationship)
                    #  print("governor", governor)
                    #  print("dependent", dependent)
                    #  print("dependency", dependency)

                    dependency.save(False)

                else:
                    # TODO: fill
                    pass

        return sentence

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

    count = 0
    sentence_count = len(parsed_text["sentences"])

    for sentence_data in parsed_text["sentences"]:
        sentence = Sentence(text = sentence_data["text"])
        position = 0

        for word_data in sentence_data["words"]:
            word = word_data[0]
            part_of_speech = word_data[1]["PartOfSpeech"]
            lemma = word_data[1]["Lemma"]

            key = (word, part_of_speech, lemma)

            space_before = " "

            try:
                if txt[int(word_data[1]["CharacterOffsetBegin"]) - 1] != " ":
                    space_before = ""
            except IndexError:
                pass

            if key in words.keys():
                word = words[key]
                # print("In dict " + str(word))

            else:
                try:
                    word = Word.query.filter_by(
                        word = word,
                        lemma = lemma,
                        part_of_speech = part_of_speech
                    ).one()
                    # print("Found word " + str(word))
                except(MultipleResultsFound):
                    print("ERROR: duplicate records found for:")
                    print("\t" + str(key))
                except(NoResultFound):
                    word = Word(
                        word = word,
                        lemma = lemma,
                        part_of_speech = part_of_speech
                    )
                    # print("New word " + str(word))

                words[key] = word

            sentence.add_word(
                word = word,
                position = position,
                space_before = space_before, # word["space_before"],
                part_of_speech = word.part_of_speech
            )

            position += 1

        paragraph.append(sentence)

        count += 1

        # NOTE: it seems the word dictionary can overload memory sometimes, so
        # this is in place to prevent it.
        # TODO: make the 50 here and in documentparser a config
        if count % 50 == 0 or count == sentence_count:
            db.session.commit()
            words = dict()

    db.session.commit()
    return paragraph

