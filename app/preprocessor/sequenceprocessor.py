"""Handle creation of sequences from sentences.
"""

import logging
from app import app
from app.models.sequence import Sequence
from app.models.word import Word
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from app.models.bigram import Bigram

from .logger import ProjectLogger

class SequenceProcessor(object):
    """Process given input into sequences, stored as bigrams.
    """

    def __init__(self, project):
        """Set up local variables for the SequenceProcessor.

        Bigrams are stored in a dictionary that is structured like so::

            {
                "primary_lemma": {
                    "secondary_lemma": bigram,
                    "secondary_lemma": bigram2,
                },
            }
        """

        self.project = project
        self.logger = logging.getLogger(__name__)
        self.project_logger = ProjectLogger(self.logger, project)
        self.bigrams = {}

    def process(self):
        """Iterate and record every bigram present.

        This function uses the xtract algorithm. In short, every lemma is a
        member of a bigram along with every lemma that is less than five
        words away from it in any given sentence.

        This method iterates over every sentence in the project and then
        iterates over every word in every sentence; each word and its sentence
        is passed on to ``get_bigrams``.
        """
        sentences = self.project.get_sentences()
        for sentence in sentences:
            for index, word in enumerate(sentence.words):
                self.get_bigrams(sentence, word, index)

    def get_bigrams(self, sentence, word, index):
        """Handle the main bigram processing.

        We use the xtract algorithm for getting bigrams. In short,
        given a word, its index, and its sentence, we create bigrams of the
        word's lemmas and lemmas that are +/- five words away.

        If we encounter a lemma that already has a bigram (stored in
        ``self.bigrams``, we increase its count.

        Arguments:
            sentence (Sentence): A sentence to get bigrams for.
            word (Word): The word to use as the primary word for the bigrams.
            index (int): The position of ``word`` in ``sentence``.
        """
        start_index = max(index - 5, 0)
        end_index = min(index + 6, len(sentence.words))

        if not word.lemma in self.bigrams:
            self.bigrams[word.lemma] = {}

        for i in range(start_index, end_index):
            if i - index == 0:
                # We don't want a bigram with two of the same words
                continue
            secondary_word = sentence.words[i]
            secondary_lemma = secondary_word.lemma
            if secondary_lemma not in self.bigrams[word.lemma]:
                self.bigrams[word.lemma][secondary_lemma] = Bigram(word,
                    secondary_word)

            self.bigrams[word.lemma][secondary_lemma].add_instance(i - index,
                sentence, False)

