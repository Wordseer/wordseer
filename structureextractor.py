"""
.. module:: StuctureExtractor
    :synopsis:
"""

import document
import json
from bs4 import BeautifulSoup

class StructureExtractor:
    def __init__(self, tokenizer, structure_file):
        """Create a new StructureExtractor.

        :param Tokenizer tokenizer: A tokenizer object
        :param str structure_file: Path to a JSON file that specifies the
        document structure.
        :return: a StructureExtractor instance
        :rtype: StructureExtractor
        """
        self.t = tokenizer
        self.structure_file = open(structure_file, "r")
        self.document_structure = json.load(self.structure_file)

    def extract(file):
        """Extract a list of Documents from a file. This method uses the
        structure_file given in the constructor for rules to identify documents.

        :param file file: The file to extract
        :return: A list of Document objects
        :rtype: list
        """
        
        documents = []
        
        #text = ""
        #with open(file.name, "r", -1) as f: # TODO: this seems a bit ridiculous
        #    for line in f:
        #        text += f.readline() + "\n"
        # TODO: was there a reason the original was written like that?

        with open(file.name, "r") as f:
            doc = BeautifulSoup(f, xml)

        units = self.extract_unit_information(self.document_structure, doc)

        for unit in units:
            d = document.Document(metadata = u.metadata,
                name = "document",
                sentences = u.sentences,
                title = u.name,
                units = u.units)
            documents.append(d)

        return documents
        

    def extract_unit_information(structure, parent_node):
        """

        :param dict structure: A JSON description of the structure
        :param Tag parent_node: A BeautifulSoup Tag of the parent node.
        :return: A list of Units
        :rtype: Unit
        """
        pass

    def makeCSSSelector(input, node):
        """

        :param string input: ??
        :param Tag node: A BeautifulSoup Tag for the node that requires a
        selector.
        :return: The css selector.
        :rtype: string
        """

        pass

    def get_sentences(structure, parent_node, tokenize):
        """

        :param dict structure: A JSON description of the structure
        :param Tag node: ?
        :param boolean tokenize:
        :return: A list of sentences.
        :rtype: list
        """

        pass

    def get_metadata(metadata_structure, node):
        """

        :param list structure: A JSON description of the structure
        :param Tag node: ?
        :return: A list of metadata
        :rtype: list
        """

        pass

    def get_xpath_attribute(xpath_pattern, attribute, node):
        """

        :param string xpath_pattern:
        :param string attribute:
        :param Tag node:
        :return: A list of strings
        :rtype: list
        """

        pass

    def get_xpath_text(xpath_pattern, node):
        """

        :param string xpath_pattern:
        :param Tag node:
        :return: A list of strings
        :rtype: list
        """
        
        pass