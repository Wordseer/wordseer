import unit

class Sentence(unit.Unit):
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
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __str__(self):
        return self.metadata.__str__() + "\n" + self.text

    def __eq__(self, other):
        return self.__dict__ == other.__dict__