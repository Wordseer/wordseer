from corenlp import StanfordCoreNLP
from dependency import Dependency
from parseproducts import ParseProducts
from tokenizer import Tokenizer

# TODO: this is inefficient, we're running the tokenizer twice. Should instead
# tie this to the tokenizer.

class Parser(object):
    """Parse dependency relationships in a sentence.
    """
    def __init__(tokenizer, max_length=30):
        """Constructor for Parser.

        :key int max_length: If the sentence is longer than this, it will not
        be parsed.
        """
        self.max_length = 30
        self.tokenizer = Tokenizer()
        #TODO: we can't count the number of words until it's already parsed
        #self.parser = self.tokenizer.parser

    def parse(sentence):
        """Parse a sentence and extract dependencies, parse trees, etc.

        :param str sentence: The sentence as a string.
        """
        parsed = self.tokenizer.parser.raw_parse(sentence)
        parsed_sentence = parsed["sentences"][0]
        products = ParseProducts()
        dependencies = []

        if len(parsed["sentences"]) > 1:
            raise ValueError("More than one sentences"
                " passed in to Parser.parse().")

        for dependency in parsed["sentences"][0]["dependencies"]:
            if dependency[2] > 1 and dependency[4] > 1: #TODO: why?
                gov_index = dependency[2] - 1
                dep_index = dependency[4] - 1
                dependencies.append(Dependency(dependency[0],
                    dependency[1],
                    gov_index,
                    parsed_sentence["words"][gov_index][1]["PartOfSpeech"]
                    dependency[3],
                    parsed_sentence["words"][dep_index][1]["PartOfSpeech"])
        
        return ParseProducts(parsed["sentences"][0]["parsetree"],
            dependencies, self.tokenizer.tokenize(sentence)[0].tagged)
