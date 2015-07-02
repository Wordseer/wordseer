# -*- coding: utf-8 -*-
"""
This module handles breaking down text into Sequence objects, which are
collections of at most four words.

The SequenceProcessor requires a database reader/writer to be initialized.
The most interesting method to the user is the process() method. This method
expects a single Sentence object, and it will extract all Sequences from
this sentence and record them in the database.
"""

import logging
from app import app
from app.models.sequence import Sequence
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
import pdb

from .logger import ProjectLogger

LEMMA = "lemma"
WORD = "word"

class SequenceProcessor(object):
    """Process given input into Sequences.
    """

    def __init__(self, project):
        """Set up local variables for the SequenceProcessor.
        """

        self.project = project
        self.previously_indexed = []
        self.logger = logging.getLogger(__name__)
        self.project_logger = ProjectLogger(self.logger, project)

    def remove_stops(self, words):
        """Remove every sort of stop from the sentences.

        :param list words: A list of WordInSentence objects.
        :return list: The list without stops.
        """

        without_stops = []
        for word in words:
            if word.word.lemma not in app.config["STOPWORDS"]:
                without_stops.append(word)

        return without_stops

    def process(self, sentence, sequence_dict=None, sequence_length=2):
        """Iterate and record every sequence with length <= `sequence_length. 
        The method records using the ReaderWriter a list of sequences present 
        in the given sentence.

        :param Sentence sentence: The sentence to process,
        :return list: A list of Sequence objects, representing the results
            of processing. These sequences are also sent to the ReaderWriter.
        """

        sequences = [] # a list of Sequences
        for i in range(0, len(sentence.words)):
            # Iterate through every word
            self.previously_indexed = []
            for j in range(i+1, len(sentence.words) + 1):
                # Check every word after the one at i
                if j - i <= sequence_length:
                    # If this word is no more than `sequence_length` words away from i,
                    # create a new Sequence
                    sequences.extend(self.get_sequence(sentence, i, j))

        # Write the sequences to the database using duplication check

        if isinstance(sequence_dict, dict):
            for sequence in sequences:
                sequence_text = sequence["sequence"]
                lemmatized = sequence["is_lemmatized"]
                has_function_words = sequence["has_function_words"]
                all_function_words = sequence["all_function_words"]
                length = len(sequence["words"])
                position = sequence["start_position"]
                words = sequence["words"]

                key = sequence_text
                if key in sequence_dict.keys():
                    sequence = sequence_dict[key]
                else:

                    try:
                        sequence = Sequence.query.\
                            filter_by(sequence = sequence_text,
                            project=self.project).one()
                    except(MultipleResultsFound):
                        self.project_logger.error("Duplicate records found "
                            "for: %s", str(key))
                    except(NoResultFound):
                        sequence = Sequence(
                            sequence = sequence_text,
                            lemmatized = lemmatized,
                            has_function_words = has_function_words,
                            all_function_words = all_function_words,
                            length = length,
                            project=self.project,
                            words = words
                        )
                        sequence.save(False)

                    sequence_dict[key] = sequence

                sentence.add_sequence(
                    sequence = sequence,
                    position = position,
                    project = self.project,
                    force = False
                )

        return sequences

    def get_sequence(self, sentence, i, j):
        """Handle the main processing part in the process() loop.

        :param Sentence sentence: A sentence object to create sequences from.
        :param int i: The index to start the sequence from, inclusive.
        :param int j: The index to stop the sequence from, exclusive.
        :return list: A list of dicts representing sequences.
        """

        sequences = []

        rel_list = sentence.word_in_sentence[i:j] # all the words
        word_list = [rel.word for rel in rel_list]

        surface_phrase = join_words(rel_list, WORD)

        if surface_phrase in self.previously_indexed:
            #If we've already seen this sentence, don't bother
            return sequences

        lemmatized_phrase = join_words(rel_list, LEMMA)
        rel_list_nostops = self.remove_stops(rel_list)
        word_list_nostops = [rel.word for rel in rel_list_nostops]
        lemmatized_phrase_nostops = join_words(rel_list_nostops, LEMMA)
        surface_phrase_nostops = join_words(rel_list_nostops, WORD)

        # TOOO: Aditi says it's possible to remove these checks, should
        # see if that's doable after the unit test is written
        has_stops = len(rel_list_nostops) < len(rel_list)
        lemmatized_has_stops = (len(lemmatized_phrase_nostops) <
            len(lemmatized_phrase))
        all_stop_words = len(rel_list_nostops) == 0
        lemmatized_all_stop_words = len(lemmatized_phrase_nostops) == 0

        # Definitely make a Sequence of the surface_phrase
        sequences.append({"start_position": i,
            "sentence_id": sentence.id,
            "document_id": sentence.document_id,
            "sequence": surface_phrase,
            "is_lemmatized": False,
            "has_function_words": has_stops,
            "all_function_words": all_stop_words,
            "words": word_list})
        self.previously_indexed.append(surface_phrase)

        # If it's not just stops, has stops, and the first word isn't a stop,
        # and it hasn't been indexed, then make a Sequence from the nostop SP
        if (has_stops and not # Should have stops to avoid duplicate
            all_stop_words and
            rel_list_nostops[0] == rel_list[0] and not
            surface_phrase_nostops in self.previously_indexed):
            sequences.append({"start_position": i,
                "sentence_id": sentence.id,
                "document_id": sentence.document_id,
                "sequence": surface_phrase_nostops,
                "is_lemmatized": False,
                "has_function_words": False,
                "all_function_words": False,
                "words": word_list_nostops})
            self.previously_indexed.append(surface_phrase_nostops)

        # Definitely make a Sequence of the lemmatized_phrase
        sequences.append({"start_position": i,
            "sentence_id": sentence.id,
            "document_id": sentence.document_id,
            "sequence": lemmatized_phrase,
            "is_lemmatized": True,
            "has_function_words": lemmatized_has_stops,
            "all_function_words": lemmatized_all_stop_words,
            "words": word_list})
        self.previously_indexed.append(lemmatized_phrase)

        # Maybe make a sequence of the lemmatized_phrase_nostop
        if (lemmatized_has_stops and not
            lemmatized_all_stop_words and
            rel_list_nostops[0] == rel_list[0] and not
            lemmatized_phrase_nostops in self.previously_indexed):
            # We don't add this to previously_indexed
            #print "Lemmatized nostop"
            #print lemmatized_phrase_nostops
            sequences.append({"start_position": i,
                "sentence_id": sentence.id,
                "document_id": sentence.document_id,
                "sequence": lemmatized_phrase_nostops,
                "is_lemmatized": True,
                "has_function_words": False,
                "all_function_words": False,
                "words": word_list_nostops})

        return sequences

def join_words(words, attr):
    """Join either lemmas or surface words from a list of `WordInSentence`
    objects.

    :param list words: A list of WordInSentence objects.
    :param str attr: Either sequenceprocessor.LEMMA to combine lemmas or
        sequenceprocessor.WORD to combine words.
    :return str: The combined sentence.
    """

    result = []

    if attr == LEMMA:
        for word in words:
            result.append(word.word.lemma)
    elif attr == WORD:
        for word in words:
            result.append(word.surface)
    return " ".join(result)

