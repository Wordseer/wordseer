# TODO: real documentation
class ParseProducts(object):
    def __init__(self, syntactic_parse, dependencies, pos_tags):
        """
        :param string syntactic_parse:
        :param list dependencies: A list of Dependencies
        :param list pos_tags: A list of TaggedWords
        """

        self.syntactic_parse = syntactic_parse
        self.dependencies = dependencies
        self.pos_tags = pos_tags

    def __str__(self):
        output = ("+++ Syntactic parse:\n" + self.syntactic_parse + "\n" +
            "+++ Typed dependencies:\n")

        for dep in self.dependencies:
            output += str(dep) + "\n"

        output += "+++ Part-of-speech tags:\n"

        for word in self.pos_tags:
            output += str(word) + "\n"

        return output
