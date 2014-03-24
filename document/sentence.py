from unit import Unit

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
        text
        words
        tagged
        lemmas
        metadata
        totalSentences
        """

        self.metadata = []
        self.text = ""

        for key, val in kwargs.items():
            setattr(self, key, val)

    def __str__(self):
        return self.metadata.__str__() + "\n" + self.text
