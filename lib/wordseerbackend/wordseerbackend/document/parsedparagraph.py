from ..mixins.comparebydict import CompareByDict
from ..mixins.kwargstodict import KwargsToDict

class ParsedParagraph(KwargsToDict, CompareByDict):
    """A container for a paragraph that has been parsed, containing both the
    original text and the result of parsing each sentence with the parser.
    """
    def __init__(self, **kwargs):
        """Instantiate a ParsedParagraph.
        
        :key list sentences: A list of Sentence objects, representing the
        sentences in this paragraph
        :key list parses: A list of ParseProducts, each representing a Sentence
        from sentences
        :key str type: ORPHAN?
        :key dict metadata: ORPHAN?
        :key int id: ORPHAN?
        :key float number: ORPHAN?
        :key int narrative_id: ORPHAN?
        :key str text: ORPHAN?
        """

        self.sentences = []
        self.parses = []
        self.metadata = {}

        super(ParsedParagraph, self).__init__(**kwargs)
        self.text = str(self)

    def add_sentence(self, sentence, parse):
        """
        Add a sentence and its ParseProducts to this ParsedParagraph.

        :param Sentence sentence: The sentence to add.
        :param ParseProducts parse: The sentence's ParseProducts.
        """
        self.sentences.append(sentence)
        self.parses.append(parse)
        self.text = str(self)

    def __str__(self):
        output = ""

        for entry, value in self.metadata.items():
            output += " (" + entry + ": " + value + ") "

        for sentence in self.sentences:
            output += str(sentence) + " "

        return output
