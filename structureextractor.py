"""
.. module:: StuctureExtractor
    :synopsis: Methods to parse XML files and generate python classes from their
    contents.
"""

from document.document import Document
from document.sentence import Sentence
from document.unit import Unit
from document.metadata import Metadata
import json
from lxml import etree
import string

class StructureExtractor(object):
    """This class parses an XML file according to the format given in a
    JSON file. It generates document classes (Sentences, Documents, Metadatas,
    etc.) from the input file.
    """
    def __init__(self, tokenizer, structure_file):
        """Create a new StructureExtractor.

        :param Tokenizer tokenizer: A tokenizer object
        :param str structure_file: Path to a JSON file that specifies the
        document structure.
        :return StructureExtractor: a StructureExtractor instance
        """
        self.t = tokenizer
        self.structure_file = open(structure_file, "r")
        self.document_structure = json.load(self.structure_file)

    def extract(self, infile):
        """Extract a list of Documents from a file. This method uses the
        structure_file given in the constructor for rules to identify documents.

        :param file/str infile: The file to extract; readable objects or paths
        as strings are acceptable.
        :return list: A list of Document objects
        """

        documents = []
        doc = etree.parse(infile)
        units = self.extract_unit_information(self.document_structure, doc)

        for extracted_unit in units:
            d = Document(metadata=extracted_unit.metadata,
                name="document",
                sentences=extracted_unit.sentences,
                title=extracted_unit.name,
                units=extracted_unit.units)
            documents.append(d)

        return documents

    def extract_unit_information(self, structure, parent_node):
        """Process the given node, according to the given structure, and return
        a list of Unit objects that represent the parent_node.

        :param dict structure: A JSON description of the structure
        :param etree parent_node: An lxml element tree of the parent node.
        :return list: A list of Units
        """
        units = []
        xpaths = structure["xpaths"]

        for xpath in xpaths:
            nodes = get_nodes_from_xpath(xpath, parent_node)
            for node in nodes:
                current_unit = Unit(name=structure["structureName"])
                # Get the metadata
                current_unit.metadata = get_metadata(structure, node)
                # If there are child units, retrieve them and put them in a
                # list, otherwise get the sentences
                children = []
                if "units" in structure.keys():
                    for child_struc in structure["units"]:
                        children.extend(
                            self.extract_unit_information(child_struc, node))
                else:
                    current_unit.sentences = self.get_sentences(structure, node,
                        True)

                current_unit.units = children
                units.append(current_unit)
        return units

    def get_sentences(self, structure, parent_node, tokenize):
        """Return the sentences present in the parent_node and its children.

        :param dict structure: A JSON description of the structure
        :param etree node: An lxml etree object of the node to get sentences
        from
        :param boolean tokenize: if True, then the sentences will be tokenized
        :return list: A list of Sentences.
        """

        result_sentences = [] # a list of sentences
        sentence_text = ""
        sentence_metadata = [] # List of Metadata objects
        unit_xpaths = structure["xpaths"]

        for xpath in unit_xpaths:
            try:
                sentence_nodes = get_nodes_from_xpath(xpath, parent_node)
            except AttributeError:
                # It's already an ElementString or some such
                sentence_nodes = parent_node.getparent().iter()

            for sentence_node in sentence_nodes:
                sentence_text += etree.tostring(sentence_node,
                    method="text").strip() + "\n"
                sentence_metadata.append(get_metadata(structure,
                    sentence_node))

        if tokenize:
            sents = self.t.tokenize(sentence_text)

            for sent in sents:
                sent.metadata = sentence_metadata
                words = string.split(" ", sent.text)
                total_word_length = 0

                for word in words:
                    total_word_length += len(word)

                result_sentences.append(sent)

        else:
            result_sentences.append(Sentence(text=sentence_text,
                metadata=sentence_metadata))
        return result_sentences


def get_metadata(structure, node):
    """Return a list of Metadata objects of the metadata of the Tags in
    node according to the rules in metadata_structure.

    If the Tags have attributes, then the value fields of the metadata
    objects will be those attributes. Otherwise, the text in the Tags
    will be the values. property_name is set according to PropertyName in
    metadata_strcuture. specification is set as the object in the JSON
    file that describes the xpath and propertyName of that Metadata object.
    This function iterates over every child of metadata in the structure
    file.

    :param list structure: A JSON description of the structure
    :param etree node: An lxml element tree to get metadata from.
    :return list: A list of Metadata objects
    """

    try:
        metadata_structure = structure["metadata"]
    except KeyError:
        return []

    metadata_list = [] # A list of Metadata

    for spec in metadata_structure:
        try:
            xpaths = spec["xpaths"]
        except KeyError:
            xpaths = []
        try:
            attribute = spec["attr"]
        except KeyError:
            attribute = None

        extracted = [] # A list of strings

        for xpath in xpaths:
            if attribute is not None:
                extracted = get_xpath_attribute(xpath,
                    attribute, node)
            else:
                extracted = get_xpath_text(xpath, node)
            for val in extracted:
                metadata_list.append(Metadata(
                    value=val,
                    property_name=spec["propertyName"],
                    specification=spec))
    return metadata_list

def get_xpath_attribute(xpath_pattern, attribute, node):
    """Return values of attribute from the child elements of node that
    match xpath_pattern.

    :param string xpath_pattern: A pattern to find matches for
    :param string attribute: The attribute whose values should be returned
    :param etree node: The node to search in
    :return list: A list of strings, the values of the attributes
    """

    values = [] # list of strings

    if len(xpath_pattern.strip()) == 0:
        vals = node.get(attribute).split(" ")
        # Split the attribute since xml does not allow multiple attributes
        if len(vals) > 0:
            for value in vals:
                values.append(value)
    else:
        nodes = node.xpath(xpath_pattern)
        for node in nodes:
            vals = node.get(attribute).split(" ")
            if len(vals) > 0:
                for val in vals:
                    values.append(val)
    return values

def get_xpath_text(xpath_pattern, node):
    """Get the text from children of node that match xpath_pattern.

    :param string xpath_pattern: The pattern to find matches for.
    :param etree node: The node to find matches under
    :return list: A list of strings, with one string for every node that matches
    xpath_pattern
    """

    values = [] # a list of strings

    if len(xpath_pattern.strip()) == 0:
        values.append(etree.tostring(node, method="text"))
    else:
        nodes = node.xpath(xpath_pattern)
        for node in nodes:
            value = str(etree.tostring(node.getparent(), method="text")).strip()
            if len(value) > 0:
                values.append(value)

    return values

def get_nodes_from_xpath(xpath, nodes):
    """If the selector is longer than 0 chars, then return the children
    of nodes that match xpath. Otherwise, return all the nodes.

    :param str xpath: The xpath to match.
    :param etree nodes: LXML etree object of nodes to search.
    :return list: The matched nodes, as ElementStringResult objects.
    """
    if len(xpath.strip()) == 0 or nodes in nodes.xpath("../" + xpath):
        return [nodes]
    return nodes.xpath(xpath)
