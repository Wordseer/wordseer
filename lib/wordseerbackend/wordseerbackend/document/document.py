"""
Document objects represent the topmost division of a file; an entire
file is considered a document.
"""

from unit import Unit

class Document(Unit):
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
        document. ORPHAN?
        :keyword string title: The title of the document.
        """

        self.title = ""
        self.metadata = []
        self.units = []
        self.sentences = []

        super(Document, self).__init__(*args, **kwargs)

    def __str__(self):
        output = "<" + self.title + ">" + str(self.metadata) + "\n"

        for unit in self.units:
            output += str(unit) + "\n"
        for sentence in self.sentences:
            output += str(sentence) + "\n"

        return output
