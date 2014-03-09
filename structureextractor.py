"""
.. module:: StuctureExtractor
    :synopsis:
"""

import json
import beautifulstonesoup

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
        """

        :param file file: The file to extract
        :return: A list of Document objects
        :rtype: list
        """
        pass

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