from unit import Unit

class Sentence(Unit):
    """
    A sentence is a type of Unit that can only contain TaggedWords.
    """

    def __init__(self, **kwargs):
        """
        Instantiate a Sentence.

        :key int id: The ID number for this sentence.
        :key float number: ORPHAN?
        :key int document_id: The ID of the document that contains this
        sentence.
        :key string text: The raw text of this sentence.
        :key list words: A list of words as strings that make up this sentence.
        :key list tagged: A list of TaggedWord objects that make up this
        sentence.
        :key list lemmas: A list of lemmas as strings for the words in this
        sentence.
        :key list metadata: A list of Metadata objects to describe this
        sentence.
        :key int total_sentences: OPRHAN?
        """

        self.metadata = []
        self.text = ""

        super(Sentence, self).__init__(**kwargs)

    def __str__(self):
        return str(self.metadata) + "\n" + self.text
