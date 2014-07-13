from .base import Base
from app import db

class ParsedParagraph(db.Model, Base):
    """A container for a paragraph that has been parsed, containing both the
    original text and the result of parsing each sentence with the parser.

    Attributes:
        sentences (list): A list of ``Sentence`` objects, representing the
            sentences in this paragraph
        parses (list): A list of ``ParseProducts``, each representing a
            ``Sentence`` from ``sentences``
        properties (list): A list of ``Properies`` that apply to this
            ``ParsedParagraph``.

    """

    #TODO: are these all one to many?
    sentences = db.relationship("Sentence", backref="parsed_paragraph")
    parses = db.relationship("ParseProducts")
    properties = db.relationship("Property", backref="parsed_paragraph")

    def add_sentence(self, sentence, parse):
        """
        Add a sentence and its ParseProducts to this ParsedParagraph.

        :param Sentence sentence: The sentence to add.
        :param ParseProducts parse: The sentence's ParseProducts.
        """
        self.sentences.append(sentence)
        self.parses.append(parse)
        self.text = str(self) #TODO: why does this happen?

