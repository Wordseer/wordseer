"""
A class to store sequences of words.
"""

class Sequence(object):
    """A Sequence is a series of words in the order in which they appeared in
    their original sentence.
    """

    def __init__(self, *args, **kwargs):
        """Instantiate a Sequence object.

        :keyword str sequence_id: The ID of this sequence.
        :keyword int start_position: Index of the first word of this
        sequence in the sentence it came from.
        :keyword int sentence_id: The ID of the sentence that this sequence
        came from.
        :keyword int document_id: The ID of the document of the sentence that
        this sequence came from.
        :keyword str sequence: The sequence of words.
        :keyword boolean is_lemmatized: If True, this sequence is a sequence of
        lemmas. If False, this is a sequence of words.
        :keyword boolean has_function_words: If True, this sequence contains
        function words, which are defined in SequenceProcessor's constructor.
        Otherwise, it does not.
        :keyword boolean all_function_words: If True, this sentence is only
        made of function words.
        :keyword int length: The number of words in this sequence.
        :keyword list words: A list of TaggedWord objects representing the words
        in this sequence. Even if this sequence is lemmatized, the TaggedWords
        contain both the original word and its lemma.
        """

        words = []

        for item, value in kwargs.items():
            setattr(self, item, value)

        self.length = len(words)
