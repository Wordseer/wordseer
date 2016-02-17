"""Methods to handle string parsing, tokenization, tagging, etc.
"""
from datetime import datetime
import json
import logging
from nltk.tokenize import sent_tokenize
import re

from app import app
from app.corenlp import StanfordCoreNLP, ProcessError, TimeoutError
from app.models.sentence import Sentence
from app.models.word import Word
from app.models.dependency import Dependency
from app.models.grammaticalrelationship import GrammaticalRelationship
from app import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from .logger import ProjectLogger


class StringProcessor(object):
    """Tokenize and parse a string.
    """

    def __init__(self, project):
        """Instantiate and ready the parser. Note that readying the parser takes
        some time.
        """
        self.parser = StanfordCoreNLP()
        self.project = project
        self.parsetime = 0

        logger = logging.getLogger(__name__)
        global project_logger
        project_logger = ProjectLogger(logger, project)

    def parse(self, text, relationships=None, dependencies=None):
        """Tokenize and parse some text to create ``Sentence`` objects and extract 
        dependencies, parse trees, etc.

        :param Sentence sentence: The ``Sentence`` object.

        """

        start_time = datetime.now()
        parsed = self.parse_with_error_handling(text)
        end_time = datetime.now()

        # If the parse was unsuccessful, exit
        if parsed == None:
            return []
        # timing report
        parsetime = end_time - start_time
        self.parsetime += parsetime.total_seconds()
        
        sentences = []

        for parsed_sentence in parsed['sentences']:
            sentence = Sentence(text = parsed_sentence['text'], project=self.project)
            sentence.save(False)

            self.add_words(sentence, parsed_sentence, text)
            self.add_grammatical_relations(sentence, parsed_sentence, relationships, dependencies)

            sentence.save(False)            
            sentences.append(sentence)
            
        return sentences

    def parse_with_error_handling(self, text):
        """Run the parser and handle errors properly.

        Also checks the sentence text for irregularities that may break the
        parser and handles it before proceeding.

        Any failure will cause this method to return None

        :param str text: The text of the sentence to check
        """

        # Check for non-string
        if not isinstance(text, str) and not isinstance(text, unicode):
            project_logger.warning("Parser got a non-string argument: %s", text)
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

    def add_words(self, sentence, parsed_sentence, raw_text):
        """Given a Sentence and its parsed text, and find the PoS, lemmas, 
        and space_befores of each word in the sentence, and add them to the
        Sentence object.
        """
        words = dict()
        position = 0
        space = re.compile(r'\s')
        cr = re.compile(r'[\n\r]')

        for word_data in parsed_sentence["words"]:
            surface = word_data[0]
            part_of_speech = word_data[1]["PartOfSpeech"]
            try:
                lemma = word_data[1]["Lemma"].lower()
            except AttributeError as err:
                # this word wasn't recognized as a word by the parser,
                # it's probably a weird character or something
                lemma = "*" * (int(word_data[1]["CharacterOffsetEnd"]) - int(word_data[1]["CharacterOffsetBegin"]))
                surface = "*" * (int(word_data[1]["CharacterOffsetEnd"]) - int(word_data[1]["CharacterOffsetBegin"]))
            space_before = ""
            try:
                prevChar = raw_text[int(word_data[1]["CharacterOffsetBegin"]) - 1]
                if space.match(prevChar):
                    if cr.match(prevChar):
                        space_before = "\n"
                    else:
                        space_before = " "
            except IndexError:
                pass

            key = (surface.lower(), part_of_speech, lemma)

            if key in words:
                word = words[key]

            else:
                try:
                    word = Word.query.filter_by(lemma=lemma, surface=surface.lower(),
                                                part_of_speech=part_of_speech).one()
                except MultipleResultsFound:
                    project_logger.warning("Duplicate records found for: %s",
                                           str(key))
                except NoResultFound:
                    word = Word(lemma=lemma, surface=surface.lower(), part_of_speech=part_of_speech)
                    word.save(False)

                words[key] = word

            sentence.add_word(
                word=word,
                position=position,
                space_before=space_before,
                surface=surface,
                project=self.project,
                force=False
            )

            position += 1

        db.session.commit()

    def add_grammatical_relations(self, sentence, parsed_sentence, relationships, dependencies):
        
        for dependency in parsed_sentence["dependencies"]:
            # We don't want to make a dependency involving ROOT
            if int(dependency[2]) > 0 and int(dependency[4]) > 0:
                governor = dependency[1]
                dependent = dependency[3]
                governor_index = int(dependency[2]) - 1
                dependent_index = int(dependency[4]) - 1
                governor_pos = parsed_sentence["words"][governor_index][1]\
                    ["PartOfSpeech"]
                try:
                    governor_lemma = parsed_sentence["words"][governor_index][1]\
                        ["Lemma"].lower()
                except AttributeError:
                    # this word wasn't recognized as a word by the parser,
                    # it's probably a weird character or something
                    governor_lemma = "*" * (int(parsed_sentence["words"][governor_index][1]["CharacterOffsetEnd"]) - int(parsed_sentence["words"][governor_index][1]["CharacterOffsetBegin"]))
                    governor = governor_lemma[:]
                dependent_pos = parsed_sentence["words"][dependent_index][1]\
                    ["PartOfSpeech"]
                try:
                    dependent_lemma = parsed_sentence["words"][dependent_index][1]\
                        ["Lemma"].lower()
                except AttributeError:
                    # this word wasn't recognized as a word by the parser,
                    # it's probably a weird character or something
                    dependent_lemma = "*" * (int(parsed_sentence["words"][dependent_index][1]["CharacterOffsetEnd"]) - int(parsed_sentence["words"][dependent_index][1]["CharacterOffsetBegin"]))
                    dependent = dependent_lemma[:]
                grammatical_relationship = dependency[0]

                # If dictionaries are present, run with duplication handling
                if relationships != None and dependencies != None:
                    key = grammatical_relationship

                    if key in relationships.keys():
                        relationship = relationships[key]
                    else:

                        try:
                            relationship = GrammaticalRelationship.query.\
                                filter_by(name=grammatical_relationship,
                                          project=self.project).one()
                        except MultipleResultsFound:
                            project_logger.error("duplicate records found "
                                                 "for: %s", str(key))
                        except NoResultFound:
                            relationship = GrammaticalRelationship(
                                name=grammatical_relationship,
                                project=self.project)

                        relationships[key] = relationship

                    # Read the data for the governor, and find the
                    # corresponding word
                    governor = Word.query.filter_by(
                        lemma=governor_lemma,
                        surface=governor.lower(),
                        part_of_speech=governor_pos).first()

                    # Same as above for the dependent in the relationship
                    dependent = Word.query.filter_by(
                        lemma=dependent_lemma,
                        surface=dependent.lower(),
                        part_of_speech=dependent_pos).first()

                    try:
                        governor.id
                        dependent.id
                    except:
                        project_logger.error(
                            "Governor or dependent not "
                            "found; giving up on parse. This likely indicates "
                            "an error in the preprocessing; rerunning the "
                            "preprocessor is recommended.")
                        project_logger.info(sentence.text)
                        
                        return #die

                    key = (relationship.name, governor.id, dependent.id)

                    if key in dependencies.keys():
                        dependency = dependencies[key]
                    else:

                        try:
                            dependency = Dependency.query.filter_by(
                                grammatical_relationship=relationship,
                                governor=governor,
                                dependent=dependent
                            ).one()
                        except MultipleResultsFound:
                            project_logger.error("duplicate records found for: %s",
                                                 str(key))
                        except NoResultFound:
                            dependency = Dependency(
                                grammatical_relationship=relationship,
                                governor=governor,
                                dependent=dependent
                            )

                        dependencies[key] = dependency

                    # Add the dependency to the sentence
                    sentence.add_dependency(
                        dependency=dependency,
                        governor_index=governor_index,
                        dependent_index=dependent_index,
                        project=self.project,
                        force=False
                    )

                    dependency.save(False)

                else:
                    # TODO: fill
                    pass
                    
        db.session.commit() 
