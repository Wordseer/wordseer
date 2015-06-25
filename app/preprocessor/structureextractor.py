"""Methods to parse XML files and generate python classes from their contents.
"""

import json
import logging

from lxml import etree
from nltk.tokenize import sent_tokenize
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from app.models import *
from app import db
from . import logger



class StructureExtractor(object):
    """This class parses an XML file according to the format given in a
    JSON file. It generates document classes (Sentences, Documents, Propertys,
    etc.) from the input file.
    """
    def __init__(self, project, structure_file):
        """Create a new StructureExtractor.

        :param Project project: A Project object
        :param str structure_file: Path to a JSON file that specifies the
            document structure.
        :return StructureExtractor: a StructureExtractor instance
        """
        self.project = project
        self.structure_file = open(structure_file, "r")
        self.document_structure = json.load(self.structure_file)
        self.logger = logging.getLogger(__name__)
        self.project_logger = logger.ProjectLogger(self.logger, self.project)

    def extract(self, infile):
        """Extract ``Document``\s from a ``DocumentFile``. This method uses the
        structure_file given in the constructor for rules to identify
        ``Document``\s.

        :param str infile: The path to the file to extract.
        :return list of DocumentFiles: The DocumentFile that contains the
            extracted documents.
        """

        # Check for unescaped special characters (tentative)
        doc = None

        try:
            doc = etree.parse(infile)
        # except(etree.XMLSyntaxError) as e:
        except etree.Error as err:
            self.project_logger.error("XML Error: %s; skipping file", str(err))

        extracted_units = self.extract_unit_information(self.document_structure, doc)
        doc_num = 0

        try:
            document_file = DocumentFile.query.filter(
                DocumentFile.path == infile
            ).one()
        except NoResultFound:
            self.project_logger.warning("Could not find file with path %s, making "
                                        "new one", infile)
            document_file = DocumentFile()
        except MultipleResultsFound:
            self.project_logger.error("Found multiple files with path %s, "
                                      "skipping.", infile)
            return DocumentFile()

        for extracted_unit in extracted_units:
            document = Document()
            document.name = "document"
            document.properties = extracted_unit.properties
            document.sentences = extracted_unit.sentences
            document.title = _get_title(document.properties)
            document.children = extracted_unit.children
            document.number = doc_num

            assign_sentences(document)
            document_file.documents.append(document)
            document.save(False)

        db.session.commit()

        return document_file

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
                current_unit.project = self.project
                # Get the metadata
                current_unit.properties = get_metadata(
                    structure, node, current_unit.name, self.project)
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
                        current_unit.sentences = self.get_sentences_from_node(structure,
                                                                              node)

                if not structure.get("combine") or len(combined_nodes) == 1:
                    # end of extraction for uncombined text nodes
                    # runs only once for combined text nodes
                    current_unit.children = children
                    current_unit.save(False)
                    units.append(current_unit)

            # this code only runs for combined text nodes
            new_sentences = self.get_sentences_from_text(combined_sentence)

            for sentence in new_sentences:
                sentence.properties = get_metadata(
                    structure, combined_nodes[0], "sentence", self.project)
                units[-1].sentences.append(sentence)

            combined_sentence = ""
            combined_nodes = []

        return units

    def get_sentences_from_text(self, text):
        """Given a string of text, split into sentences and return Sentence objects.

        Arguments:
            text (str): The text to get sentences from, at least one sentence.

        Returns:
            A list of ``Sentence`` objects with ``Sentence.text`` set to the text 
            of the sentence, and reference to the Project.
        """
        sentences = []

        for sentence in split_sentences(text):
            sentences.append(Sentence(text=sentence, project=self.project))

        return sentences


    def get_sentences_from_node(self, structure, parent_node):
        """Return the sentences present in the parent_node and its children.

        :param dict structure: A JSON description of the structure
        :param etree node: An lxml etree object of the node to get sentences
            from.
        :param boolean tokenize: if True, then the sentences will be tokenized
        :return list: A list of Sentences.
        """

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
                node_text = get_xml_text(sentence_node)

                if node_text != None:
                    sentence_text += node_text.strip() + "\n"
                    sentence_metadata.extend(
                        get_metadata(structure, sentence_node, "sentence", self.project))

        sentences = self.get_sentences_from_text(sentence_text)

        for sentence in sentences:
            sentence.properties = sentence_metadata
            result_sentences.append(sentence)

        return result_sentences

def get_metadata(structure, node, unit_type, project):
    """Return a list of Property objects of the metadata of the Tags in
    node according to the rules in metadata_structure.

    If the Tags have attributes, then the value fields of the metadata
    objects will be those attributes. Otherwise, the text in the Tags
    will be the values. property_name is set according to PropertyName in
    metadata_strcuture. This function iterates over every child of metadata in
    the structure file.

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
        xpaths = spec.get("xpaths", [])
        attribute = spec.get("attr")
        data_type = spec.get("dataType")
        date_format = spec.get("dateFormat")
        property_name = spec.get("propertyName")
        metadata = PropertyMetadata.query.filter(
            PropertyMetadata.property_name == property_name).first()
        if metadata is None:
            metadata = PropertyMetadata(
                property_name=property_name,
                data_type=data_type,
                date_format=date_format,
                is_category=spec.get("isCategory"),
                display_name=spec.get("displayName"),
                display=spec.get("valueIsDisplayed"),
                unit_type=unit_type)
            metadata.save()

        extracted = [] # A list of strings

        for xpath in xpaths:
            if attribute not in [None, ""]:
                extracted = get_xpath_attribute(xpath, attribute, node)
            else:
                extracted = get_xpath_text(xpath, node)
            for val in extracted:
                prop = Property(
                    project=project,
                    value=val,
                    name=property_name,
                    property_metadata=metadata)
                metadata_list.append(prop)

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

            # Adding temporary unicode check for now, could do something else later
            value = get_xml_text(node)

            # If parse failed, skip
            if value == None:
                continue

            if len(value) > 0:
                values.append(value)

    return values

def get_xml_text(node, encoding="utf-8", method="text"):
    """Get the text from a etree node.

    Skips the node if there is a decode error.
    """

    try:
        return unicode(etree.tostring(node, encoding=encoding, method=method)).strip()
    except UnicodeDecodeError:
        return None

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

def _get_title(properties):
    """From a list of properties, retrieve the title property and return the
    value.
    """

    for prop in properties:
        if prop.name == "title":
            return prop.value

    # If there's no title property, return ` string
    return ""

def assign_sentences(document):
    """Populates the all_sentences relationship for the document.

    :param Document document: The document to use
    """

    document.all_sentences = _assign_sentence_metadata(document, [])

def _assign_sentence_metadata(unit, all_parent_properties):
    """Recursively traverse the unit tree for sentences.

    :param Unit unit: The unt to use
    :return list: A nested list of sentences
    """
    properties = all_parent_properties[:]
    properties.extend(unit.properties)
    sentences = list(unit.sentences)
    for sentence in sentences:
        for prop in properties:
            property_of_sentence = PropertyOfSentence(
                property=prop,
                sentence=sentence)
            property_of_sentence.save()
            
    for child in unit.children:
        sentences.extend(_assign_sentence_metadata(child, properties))
    return sentences

def split_sentences(text):
    """Split the string into sentences.

    Also runs a length check and splits sentences that are too long on
    reasonable punctuation marks.

    :param str text: The text to split
    """

    sentences = []

    # Split sentences using NLTK
    sentence_texts = sent_tokenize(text)

    for sentence_text in sentence_texts:

        # Check length of sentence
        max_length = app.config["SENTENCE_MAX_LENGTH"]
        truncate_length = app.config["LOG_SENTENCE_TRUNCATE_LENGTH"]
        approx_sentence_length = len(sentence_text.split(" "))

        if approx_sentence_length > max_length:
            project_logger.warning("Sentence appears to be too long, max "
                "length is %s: %s", str(max_length),
                sentence_text[:truncate_length] + "...")

            # Attempt to split on a suitable punctuation mark
            # Order (tentative): semicolon, double-dash, colon, comma

            # Mini helper function to get indices of punctuation marks

            split_characters = app.config["SPLIT_CHARACTERS"]
            subsentences = None

            for character in split_characters:
                subsentences = sentence_text.split(character)

                # If all subsentences fit the length limit, exit the loop
                if all([len(subsentence.split(" ")) <= max_length
                    for subsentence in subsentences]):

                    project_logger.info("Splitting sentence around %s to fit "
                        "length limit.", character)
                    break

                # Otherwise, reset subsentences and try again
                else:
                    subsentences = None

            # If none of the split characters worked, force split on max_length
            if not subsentences:
                project_logger.warning("No suitable punctuation for " +
                    "splitting; forcing split on max_length number of words")
                subsentences = []
                split_sentence = sentence_text.split(" ")

                index = 0
                # Join every max_length number of words
                while index < approx_sentence_length:
                    subsentences.append(" ".join(
                        split_sentence[index:index+max_length]))
                    index += max_length

            sentences.extend(subsentences)

        else:
            sentences.append(sentence_text)

    return sentences