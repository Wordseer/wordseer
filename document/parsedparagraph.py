from mixins.kwargstodict import KwargsToDict
#TODO: documentation
class ParsedParagraph(KwargsToDict):
    def __init__(self, **kwargs):
        """
        :param list sentences:
        :param list parses:
        :param str type:
        :param dict metadata:
        :param int id:
        :param float number:
        :param int narrative_id:
        :param str text:
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
