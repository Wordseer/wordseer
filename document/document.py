import unit

class Document(unit.Unit):
    """Store information about a Document."""
    
    def __init__(self, *args, **kwargs):
        """Instantiate a new Document.

        :keyword list metadata: A list of Metadata objects that apply to this
        Document.
        :keyword list units: A list of Units that this document has, if any.
        :keyword list sentences: A list of Sentences that this document has,
        if any.
        :keyword int id: An ID for this document.
        :keyword int total_sentences: The total number of sentences for the
        document.
        :keyword string title: The title of the document.
        """

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        s = "<" + self.title + ">" + str(metadata) + "\n"
        
        for unit in self.units:
            s += str(unit) + "\n"
        for sentence in self.sentences:
            s += str(sent) + "\n"

        return s

    def __eq__(self, other):
        return self.__dict__ == other.__dict__