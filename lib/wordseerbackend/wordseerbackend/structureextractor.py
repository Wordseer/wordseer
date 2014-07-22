"""
.. module:: StuctureExtractor
    :synopsis: Methods to parse XML files and generate python classes from their
    contents.
"""

import json
from lxml import etree

from app.models.document import Document
from app.models.sentence import Sentence
from app.models.unit import Unit
from app.models.property import Property

class StructureExtractor(object):
    """This class parses an XML file according to the format given in a
    JSON file. It generates document classes (Sentences, Documents, Propertys,
    etc.) from the input file.
    """
    def __init__(self, str_proc, structure_file):
        """Create a new StructureExtractor.

        :param StringProcessor str_proc: A StringProcessor object
        :param str structure_file: Path to a JSON file that specifies the
            document structure.
        :return StructureExtractor: a StructureExtractor instance
        """
        self.str_proc = str_proc
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

        doc_num = 0
        for extracted_unit in units:
            d = Document(properties=extracted_unit.properties,
                sentences=extracted_unit.sentences,
                title=extracted_unit.name,
                children=extracted_unit.children,
                number = doc_num)
            assign_sentences(d)

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
        combined_sentence = ""
        combined_nodes = []

        for xpath in xpaths:
            nodes = get_nodes_from_xpath(xpath, parent_node)
            for node in nodes:
                current_unit = Unit(name=structure["structureName"])
                # Get the metadata
                current_unit.properties = get_metadata(structure, node)
                # If there are child units, retrieve them and put them in a
                # list, otherwise get the sentences
                children = []
                if "units" in structure.keys():
                    for child_struc in structure["units"]:
                        children.extend(self.extract_unit_information(
                            child_struc,
                            node))
                else:
                    if structure.get("combine") == True:
                        # This element contains text which must be combined
                        # with the next sibling element of this type.
                        combined_sentence += str(node) + " "
                        combined_nodes.append(node)
                    else:
                        current_unit.sentences = self.get_sentences(structure,
                            node, True)

                if not structure.get("combine") or len(combined_nodes) == 1:
                    current_unit.children = children
                    current_unit.save()
                    units.append(current_unit)

            # TODO: refactor, this code is similar in get_sentences
            new_sentences = self.get_sentences_from_text(combined_sentence,
                True)

            for sentence in new_sentences:
                sentence.properties = get_metadata(structure, combined_nodes[0])
                units[-1].sentences.append(sentence)

            combined_sentence = ""
            combined_nodes = []

        return units

    def get_sentences_from_text(self, text, tokenize):
        """Given a string of text, either tokenize the sentences and return
        the result or return the given string.

        Arguments:
            text (str): The text to get sentences from, at least one sentence.
            tokenize (boolean): Whether or not to tokenize the sentence.

        Returns:
            If ``tokenize`` is ``True`` a list of ``Sentence`` objects with
            ``Sentence.text`` set to the text of the sentence.

            Otherwise, return a list of one ``Sentence`` object with
            ``Sentence.text`` set to ``text``.
        """
        if not tokenize:
            return [Sentence(text=text)]

        else:
            return self.str_proc.tokenize(text)

    def get_sentences(self, structure, parent_node, tokenize):
        """Return the sentences present in the parent_node and its children.

        :param dict structure: A JSON description of the structure
        :param etree node: An lxml etree object of the node to get sentences
            from.
        :param boolean tokenize: if True, then the sentences will be tokenized
        :return list: A list of Sentences.
        """
        #TODO: do we really need the tokenize argument?

        result_sentences = [] # a list of sentences
        sentence_text = ""
        sentence_metadata = [] # List of Property objects
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
                sentence_metadata.extend(get_metadata(structure,
                    sentence_node))

#        if tokenize:
#            sents = self.str_proc.tokenize(sentence_text)
#            for sent in sents:
#                sent.properties = sentence_metadata
#                result_sentences.append(sent)
#
#        else:
#            result_sentences.append(Sentence(text=sentence_text,
#                metadata=sentence_metadata))
        sentences = self.get_sentences_from_text(sentence_text, tokenize)

        for sentence in sentences:
            # TODO: figure out sentence properties
            # sentence.properties = sentence_metadata
            result_sentences.append(sentence)

        return result_sentences

def get_metadata(structure, node):
    """Return a list of Property objects of the metadata of the Tags in
    node according to the rules in metadata_structure.

    If the Tags have attributes, then the value fields of the metadata
    objects will be those attributes. Otherwise, the text in the Tags
    will be the values. property_name is set according to PropertyName in
    metadata_strcuture. specification is set as the object in the JSON
    file that describes the xpath and propertyName of that Property object.
    This function iterates over every child of metadata in the structure
    file.

    :param list structure: A JSON description of the structure
    :param etree node: An lxml element tree to get metadata from.
    :return list: A list of Property objects
    """

    try:
        metadata_structure = structure["metadata"]
    except KeyError:
        return []

    metadata_list = [] # A list of Property

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
                metadata_list.append(Property(
                    value=val,
                    name=spec["propertyName"],
                ))
    return metadata_list

def get_xpath_attribute(xpath_pattern, attribute, node):
    """Return values of attribute from the child elements of node that
    match xpath_pattern. If there is no xpath_pattern, then the attributes of
    the root element are selected. If the attribute has spaces, it is split
    along the spaces into several list elements.

    :param string xpath_pattern: A pattern to find matches for
    :param string attribute: The attribute whose values should be returned
    :param etree node: The node to search in
    :return list: A list of strings, the values of the attributes
    """

    values = [] # list of strings

    if len(xpath_pattern.strip()) == 0:
        # this is guaranteed to be one element, it also keeps problems from
        # happening if it's a file rather than an element
        nodes = node.xpath(".")
    else:
        nodes = node.xpath(xpath_pattern)

    for node in nodes:
        attr = node.get(attribute)
        if attr is not None:
            vals = attr.split(" ")
            # Split the attribute since xml does not allow multiple attributes
            for value in vals:
                values.append(value)

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

def assign_sentences(document):
    """Populates the all_sentences relationship for the document.

    :param Document document: The document to use
    """

    document.all_sentences = _get_sentences(document)

def _get_sentences(unit):
    """Recursively traverse the unit tree for sentences.

    :param Unit unit: The unt to use
    :return list: A nested list of sentences
    """

    if not unit.children:
        return unit.sentences

    else:
        sentences = list(unit.sentences)

        for child in unit.children:
            sentences.extend(_get_sentences(child))

        return sentences
