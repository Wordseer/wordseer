import Unit

class Sentence(Unit):
    """
    A sentence is a type of Unit that can only contain words.
    """

    def __init__(self, *args, **kwargs):
        """
        Instantiate a Sentence.

        Keyword arguments:
        id
        number
        document_id
        sentence
        words
        tagged
        lemmas
        metadata
        totalSentences
        """
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __str__(self):
        return this.metadata.__str__() + "\n" + sentence