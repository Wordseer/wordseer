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

        super(Sentence, self).__init__(**kwargs)

    def __str__(self):
        return str(self.metadata) + "\n" + self.text
