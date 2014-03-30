from mixins.kwargstodict import KwargsToDict
#TODO: documentation
class ParsedParagraph(KwargsToDict):
    def __init__(self, **kwargs):
        """
        :key list sentences:
        :key list parses:
        :key str type:
        :key dict metadata:
        :key int id:
        :key float number:
        :key int narrative_id:
        :key str text:
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
