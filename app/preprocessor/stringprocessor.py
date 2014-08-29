"""Methods to handle string parsing, tokenization, tagging, etc.
"""
from nltk.tokenize import sent_tokenize
from corenlp import StanfordCoreNLP, ProcessError, TimeoutError
import logging

from app import app
from app.models.sentence import Sentence
from app.models.word import Word
from app.models.dependency import Dependency
from app.models.grammaticalrelationship import GrammaticalRelationship
from app import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from .logger import ProjectLogger
import pdb

class StringProcessor(object):
    """Tokenize or parse a string.
    """

    def __init__(self, project):
        """Instantiate and ready the parser. Note that readying the parser takes
        some time.
        """
        self.parser = StanfordCoreNLP(app.config["CORE_NLP_DIR"])
        self.project = project

        logger = logging.getLogger(__name__)
        global project_logger
        project_logger = ProjectLogger(logger, project)

    def tokenize(self, txt):
        """Turn a string of one or more ``Sentence``\s into a list of
        ``Sentence`` objects. This method will also tokenize each word in txt,
        find its PoS, lemma, and space_before.

        :param str txt: One or more sentences, in a string format.
        :return list: A list of document.Sentence objects.
        """
        sentences = []

        for sentence_text in split_sentences(txt):
            sentence = self.parse_with_error_handling(sentence_text)
            sentences.extend(tokenize_from_raw(sentence, sentence_text,
                self.project))

        return sentences

    def parse(self, sentence, relationships=None, dependencies=None,
            max_length=30):
        """Parse a ``Sentence`` and extract dependencies, parse trees, etc.

        Note that for max_length, a "word" is defined as something with a space
        on at least one side. This is not the typical definition of "word".
        This is done so that length can be checked before resources are
        committed to processing a very long sentence.

        :param Sentence sentence: The ``Sentence`` object.
        :param int max_length: The most amount of words to process.
        """

        parsed = self.parse_with_error_handling(sentence.text)

        # If the parse was unsuccessful, exit
        if parsed == None:
            return

        parsed_sentence = parsed["sentences"][0]

        if len(parsed["sentences"]) > 1:
            project_logger.warning("More than one sentence passed in to"
                " StringProcessor.parse().")
            parsed_sentence["text"] += parsed["sentences"][1]["text"]

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
                            relationship = GrammaticalRelationship.query.\
                                filter_by(name = grammatical_relationship).\
                                one()
                        except(MultipleResultsFound):
                            project_logger.error("duplicate records found "
                                "for: %s", str(key))
                        except(NoResultFound):
                            relationship = GrammaticalRelationship(
                                name = grammatical_relationship)

                        relationships[key] = relationship

                    #TODO: make this a try except
                    # Read the data for the governor, and find the
                    # corresponding word
                    governor = Word.query.\
                        filter_by(lemma=governor_lemma.lower()).\
                        first()

                    # Same as above for the dependent in the relationship
                    dependent = Word.query.\
                        filter_by(lemma=dependent_lemma.lower()).\
                        first()

                    try:
                        governor.id
                        dependent.id
                    except:
                        project_logger.error("Governor or dependent not "
                            "found; giving up on parse. This likely indicates"
                            " an error in the preprocessing; rerunning the "
                            "preprocessor is recommended.")
                        project_logger.info(sentence)
                        return sentence

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
                            self.logg_error(("duplicate records found for: %s",
                                str(key)))
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
                        project = self.project,
                        force = False
                    )

                    dependency.save(False)

                else:
                    # TODO: fill
                    pass

        return sentence

    def parse_with_error_handling(self, text):
        """Run the parser and handle errors properly.

        Also checks the sentence text for irregularities that may break the
        parser and handles it before proceeding.

        Any failure will cause this method to return None

        :param str text: The text of the sentence to check
        """

        # Check for non-string
        if not isinstance(text, str) and not isinstance(text, unicode):
            project_logger.warning("Parser got a non-string argument: %s",
                text)
            return None

        # Check for non-unicode
        if not isinstance(text, unicode):

            # Try to convert the string to unicode if possible
            # Unit test: should fail with this example:
            # http://stackoverflow.com/questions/6257647/convert-string-to-unicode

            try:
                text = unicode(text)
            except(UnicodeDecodeError):
                project_logger.warning("The following sentence text is "
                    "not unicode; convertion failed.")
                project_logger.info(text)

                # Skip sentence if flag is True
                if app.config["SKIP_SENTENCE_ON_ERROR"]:
                    return None
                else:
                    # Try to parse the sentence anyway
                    project_logger.warning("Attempting to parse "
                        "non-unicode sentence.")

        # Check for empty or nonexistent text
        if text == "" or text == None:
            return None

        # Check for irregular characters
        # TODO: what are considered irregular characters?

        # Try to parse, catch errors
        parsed_text = None
        try:
            parsed_text = self.parser.raw_parse(text)
        # TODO: handle all errors properly
        # ProcessError, TimeoutError, OutOfMemoryError
        except TimeoutError as e:
            project_logger.error("Got a TimeoutError: %s", str(e))
            return None
        except ProcessError as e:
            project_logger.error("Got a ProcessError: %s", str(e))
            return None
        except:
            project_logger.error("Unknown error")
            return None

        # Parse successful, return parsed text
        return parsed_text

def split_sentences(text):
    """Split the string into sentences.

    Also runs a length check and splits sentences that are too long on
    reasonable punctuation marks.

    :param str text: The text to split
    """

    sentences = []

    # Split sentences using NLTK
    sentence_texts = sent_tokenize(text)

    for sentence_text in sentence_texts:

        # Check length of sentence
        max_length = app.config["SENTENCE_MAX_LENGTH"]
        truncate_length = app.config["LOG_SENTENCE_TRUNCATE_LENGTH"]
        approx_sentence_length = len(sentence_text.split(" "))

        if approx_sentence_length > max_length:
            project_logger.warning("Sentence appears to be too long, max "
                "length is %s: %s", str(max_length),
                sentence_text[:truncate_length] + "...")

            # Attempt to split on a suitable punctuation mark
            # Order (tentative): semicolon, double-dash, colon, comma

            # Mini helper function to get indices of punctuation marks

            split_characters = app.config["SPLIT_CHARACTERS"]
            subsentences = None

            for character in split_characters:
                subsentences = sentence_text.split(character)

                # If all subsentences fit the length limit, exit the loop
                if all([len(subsentence.split(" ")) <= max_length
                    for subsentence in subsentences]):

                    project_logger.info("Splitting sentence around %s to fit "
                        "length limit.", character)
                    break

                # Otherwise, reset subsentences and try again
                else:
                    subsentences = None

            # If none of the split characters worked, force split on max_length
            if not subsentences:
                project_logger.warning("No suitable punctuation for " +
                    "splitting; forcing split on max_length number of words")
                subsentences = []
                split_sentence = sentence_text.split(" ")

                index = 0
                # Join every max_length number of words
                while index < approx_sentence_length:
                    subsentences.append(" ".join(
                        split_sentence[index:index+max_length]))
                    index += max_length

            sentences.extend(subsentences)

        else:
            sentences.append(sentence_text)

    return sentences

def tokenize_from_raw(parsed_text, txt, project):
    """Given the output of a call to raw_parse, produce a list of Sentences
    and find the PoS, lemmas, and space_befores of each word in each sentence.

    This method does the same thing as tokenize(), but it accepts already parsed
    data.

    :param dict parsed_text: The return value of a call to raw_parse
    :param str txt: The original text.
    :return list: A list of document.Sentence objects.
    """

    # If parsed_text is the result of a failed parse, return with an empty list
    if not parsed_text:
        return []

    paragraph = [] # a list of Sentences
    words = dict()

    count = 0
    sentence_count = len(parsed_text["sentences"])

    for sentence_data in parsed_text["sentences"]:
        sentence = Sentence(text = sentence_data["text"])
        position = 0

        for word_data in sentence_data["words"]:
            surface_word = word_data[0]
            part_of_speech = word_data[1]["PartOfSpeech"]
            lemma = word_data[1]["Lemma"].lower()

            space_before = " "

            try:
                if txt[int(word_data[1]["CharacterOffsetBegin"]) - 1] != " ":
                    space_before = ""
            except IndexError:
                pass

            #TODO: project specific
            try:
                word = Word.query.filter_by(lemma=lemma).one()
            except MultipleResultsFound:
                pdb.set_trace()
                project_logger.warning("Duplicate records found for: %s, "
                    "this should never happen.", str(lemma))
            except NoResultFound:
                word = Word(lemma=lemma)

            sentence.add_word(
                word = word,
                surface = surface_word,
                position = position,
                space_before = space_before,
                part_of_speech = part_of_speech,
                project = project,
                force=False
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

