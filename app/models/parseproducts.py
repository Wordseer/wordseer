"""Container for output of Parser.parse.
"""

from app import db
from .base import Base
from .mixins import NonPrimaryKeyEquivalenceMixin

class ParseProducts(db.Model, Base, NonPrimaryKeyEquivalenceMixin):
    """This class is a container for the results of parse(). It contains
    a string description of the parse tree, a list of the dependency
    relationships in the parsed sentence, and a list of tagged words in the
    parsed sentence.
    """

    #TODO: all these all one-to-many?
    syntactic_parse = db.Column(db.String)
    parse_id = db.Column(db.Integer, db.ForeignKey("parsed_paragraph.id"))
    dependencies = db.Column(db.PickleType)
    words = db.relationship("Word")

    def __init__(self, syntactic_parse, dependencies, pos_tags):
        """Instantiate a ParseProducts instance.

        :param string syntactic_parse: A string that describes the parse tree.
        :param list dependencies: A list of Dependencies that were present
        in the parsed sentence.
        :param list pos_tags: A list of TaggedWords that were present in the
        parsed sentence.
        """

        self.syntactic_parse = syntactic_parse
        self.dependencies = dependencies
        self.words = pos_tags

    def __str__(self):
        output = ("+++ Syntactic parse:\n" + self.syntactic_parse + "\n" +
            "+++ Typed dependencies:\n")

        for dep in self.dependencies:
            output += str(dep) + "\n"

        output += "+++ Part-of-speech tags:\n"

        for word in self.pos_tags:
            output += str(word) + "\n"

        return output

