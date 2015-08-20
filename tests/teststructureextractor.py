"""Tests for structureextractor.py.
"""

import unittest
import json

from lxml import etree
import mock

from app.models.property import Property
from app.models.sentence import Sentence
from app.models.documentfile import DocumentFile
from app.preprocessor.structureextractor import *
from app.preprocessor.stringprocessor import StringProcessor
import database

string_processor = StringProcessor(Project())

class CommonTests(object):
    """Functionality common to all extractor test cases.
    """
    def setUp(self, path, structure_file, input_file):
        """Set up some common variables.

        :param str path: The path that contains both the structure_file and
            input_file.
        :param str structure_file: The file with a JSON description of the
            XML structure.
        :param str input_file: The XML file to test.

        """
        database.clean()
        self.path = path
        self.structure_file = path + structure_file
        self.input_file = path + input_file

        string_processor.project = Project()

        self.input_project = Project()
        self.input_project.document_files.append(
            DocumentFile(path=self.input_file))
        self.input_project.save()

        with open(self.structure_file) as f:
            self.json = json.load(f)

        self.xml = etree.parse(self.input_file)
        self.extractor = StructureExtractor(self.input_project,
            self.structure_file, string_processor)

class PostTests(CommonTests, unittest.TestCase):
    """Run tests based on a single post from the articles directory.
    """
    def setUp(self):
        """Set up variables for the PostTests.
        """
        self.xpaths = ["./author",
            "./title",
            "./time",
            "./number",
            "./tags/tag",
            "   "]
        self.meta = {"time": "2012-02-23",
            "author": "rachel",
            "title": "Post 1",
            "number": "1",
            "tag": ["Tag 0", "Tag 3"]
            }
        self.sentence_contents = "This is the text of post 1. I love clouds."
        super(PostTests, self).setUp(
            "tests/data/articles/", "structure.json", "post1.xml")

    def test_extract(self):
        """Tests for extract().
        """
        document_file = self.extractor.extract(self.input_file)

        # Should only be one document
        assert len(document_file.documents) == 1
        document = document_file.documents[0]

        # NOTE: skipping because documents have actual titles now
        # Check to make sure the name and title are correct
        # self.failUnless(document.title == self.json["structureName"])
        # Should be one document, with the right sentences
        self.failUnless(len(document.children) == 1)

        extract_sentences = [sent.text for sent in
            document.children[0].sentences]
        unit_sentences = [sent.text for sent in
            self.extractor.extract_unit_information(self.json,
                self.xml)[0].children[0].sentences]

        self.failUnless(unit_sentences == extract_sentences)
        # Only two sentences in this doc
        self.failUnless(len(document.children[0].sentences) == 2)
        for sent in document.children[0].sentences:
            self.failUnless(sent.text in self.sentence_contents)
        # Check to make sure metadata is properly extracted
        self.failUnless(compare_metadata(self.meta, document.properties))

    def test_extract_unit_information(self):
        """Tests for extract_unit_information.
        """
        rootinfo = self.extractor.extract_unit_information(self.json,
            self.xml.getroot())

        #TODO: could we check that these are equivalent? sqlalchemy is
        # being weird about it
        #fileinfo = self.extractor.extract_unit_information(self.json, self.xml)

        doc_info = rootinfo[0]
        # Should only be one unit present
        self.failUnless(len(rootinfo) == 1)
        # It should be named correctly
        self.failUnless(doc_info.name == self.json["structureName"])
        # It should have no sentences
        self.failUnless(doc_info.sentences == [])
        # It should have metadata
        for meta in doc_info.properties:
            self.failUnless(isinstance(meta, Property))
        # It should only contain one other unit
        print doc_info.children
        self.failUnless(len(doc_info.children) == 1)
        sent_info = doc_info.children[0]
        # The sentence should be named correctly
        self.failUnless(sent_info.name ==
            self.json["units"][0]["structureName"])
        # It should have two sentences
        self.failUnless(len(sent_info.sentences) == 2)
        # And the sentences should have the right text
        for sent in sent_info.sentences:
            self.failUnless(isinstance(sent, Sentence))
            self.failUnless(sent.text in self.sentence_contents)

    def test_combine(self):
        expected_sentences = ["This is the text of post 3.",
            "I love blogs, but I also love debugging.",
            "Debugging is the best."]
        mock_get_sentences_dict = {"This is the text of post 3. I love blogs, "
            "but I also love debugging. Debugging is the best":
                expected_sentences}

        fileinfo = self.extractor.extract_unit_information(self.json,
            etree.parse(self.path + "post2.xml"))

        sentences = fileinfo[0].children[0].sentences

        actual_sentences = [sentence.text for sentence in sentences]
        assert actual_sentences == expected_sentences

    def test_get_metadata(self):
        """Tests for get_metadata
        """
        results = get_metadata(self.json, self.xml.getroot(), "sentence", None)
        self.failUnless(compare_metadata(self.meta, results))

    def test_get_xpath_attribute(self):
        """Test get_xpath_attribute.
        """
        self.failUnless(get_xpath_attribute("./tags/tag", "attribute",
            self.xml) == ["value"])
        self.failUnless(get_xpath_attribute("", "attribute",
            self.xml) == ["value1"])
        self.failUnless(get_xpath_attribute("", "blankval",
            self.xml) == [""])
        self.failUnless(get_xpath_attribute("", "multival",
            self.xml) == ["one", "two"])
        self.failUnless(get_xpath_attribute("", "nonexistant",
            self.xml) == [])

    def test_get_xpath_text(self):
        """Tests for get_xpath_text
        """
        texts = [["rachel"],
            ["Post 1"],
            ["2012-02-23"],
            ["1"],
            ["Tag 0", "Tag 3"],
            ["\n2012-02-23\nPost 1\nrachel\n\n Tag 0\n Tag " +\
                "3\n\n1\n\n\tThis is the text of post 1. I love clouds.\n\n"]]
        key = dict(zip(self.xpaths, texts))
        for xpath, text in key.items():
            result = get_xpath_text(xpath, self.xml.getroot())
            self.failUnless(result == text)

class PlayTests(CommonTests, unittest.TestCase):
    """Tests based on an abbreviated version of a play.
    """
    def setUp(self):
        """Set up local variables.
        """
        super(PlayTests, self).setUp(
            "tests/data/plays/", "structure.json", "brief_example.xml")

    @unittest.skip("Whatever this was testing is way outdated, need to start over")
    def test_get_sentences_from_node(self):
        """Test get_sentences_from_node
        """
        #Test more cases?
        print self.extractor.get_sentences_from_node(
            self.json["units"][0], self.xml.getroot()
            )
        # [0].text
        print etree.tostring(self.xml.getroot()[5], method="text").strip() + "\n"
        
        self.failUnless(self.extractor.get_sentences_from_node(self.json["units"][0],
            self.xml.getroot())[0].text == etree.tostring(
            self.xml.getroot()[5], method="text").strip() + "\n")

class LongSentenceTests(CommonTests, unittest.TestCase):
    """Tests specific to documents with long sentences that need to be split.
    """
    def setUp(self):
        """shouldn't have to do any database stuff to make this work
        """
        pass

    def test_split_paragraph(self):
        """Tests for split_paragraph()"""
        
        # short sentences should pass through
        short_sentence = " lacinia metus at, ullamcorper arcu Sed eu vestibulum lectus, sed pulvinar tortor Donec euismod lobortis diam ac ullamcorper Nullam aliquet sagittis tellus, vel pellentesque justo tristique sed Curabitur lacinia sagittis odio, ut hendrerit elit aliquam pellentesque Fusce aliquet odio eget est dapibus, aliquet auctor dolor aliquam Proin id nisl consectetur, euismod velit id, placerat urna Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas Nullam in facilisis augue Nullam vel porta tellus Pellentesque aliquam ante in bibendum tincidunt."
        expected = [short_sentence]
        result = split_paragraph(short_sentence)
        self.assertEqual(result, expected)

        # long sentences should split on punctuation
        # semicolon has higher priority than comma
        long_sentence_with_punc = "Lorem ipsum dolor sit amet, consectetur adipiscing elit Phasellus sit amet maximus tellus, id dapibus urna Quisque risus mi, volutpat ut dui sit amet, aliquet accumsan quam Integer elementum quis ipsum non elementum Etiam ac lorem mauris Lorem ipsum dolor sit amet, consectetur adipiscing elit Mauris augue lectus, volutpat eu vehicula ac, ullamcorper eget metus Vestibulum vitae metus consectetur, viverra lectus nec, cursus risus Suspendisse est enim, hendrerit mollis molestie ut, vestibulum nec lorem Nulla vel mi malesuada; lacinia metus at, ullamcorper arcu Sed eu vestibulum lectus, sed pulvinar tortor Donec euismod lobortis diam ac ullamcorper Nullam aliquet sagittis tellus, vel pellentesque justo tristique sed Curabitur lacinia sagittis odio, ut hendrerit elit aliquam pellentesque Fusce aliquet odio eget est dapibus, aliquet auctor dolor aliquam Proin id nisl consectetur, euismod velit id, placerat urna Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas Nullam in facilisis augue Nullam vel porta tellus Pellentesque aliquam ante in bibendum tincidunt."
        
        expected = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit Phasellus sit amet maximus tellus, id dapibus urna Quisque risus mi, volutpat ut dui sit amet, aliquet accumsan quam Integer elementum quis ipsum non elementum Etiam ac lorem mauris Lorem ipsum dolor sit amet, consectetur adipiscing elit Mauris augue lectus, volutpat eu vehicula ac, ullamcorper eget metus Vestibulum vitae metus consectetur, viverra lectus nec, cursus risus Suspendisse est enim, hendrerit mollis molestie ut, vestibulum nec lorem Nulla vel mi malesuada;",
            " lacinia metus at, ullamcorper arcu Sed eu vestibulum lectus, sed pulvinar tortor Donec euismod lobortis diam ac ullamcorper Nullam aliquet sagittis tellus, vel pellentesque justo tristique sed Curabitur lacinia sagittis odio, ut hendrerit elit aliquam pellentesque Fusce aliquet odio eget est dapibus, aliquet auctor dolor aliquam Proin id nisl consectetur, euismod velit id, placerat urna Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas Nullam in facilisis augue Nullam vel porta tellus Pellentesque aliquam ante in bibendum tincidunt."
        ]

        result = split_paragraph(long_sentence_with_punc)
        self.assertEqual(result, expected, msg=result)

        # if there's no suitable punctuation, long sentence should just split on word bounds
        long_sentence_no_punc = "Nullam nec egestas purus Aliquam tincidunt in enim nec egestas Donec eget nunc vitae turpis mollis ultricies in vitae turpis Proin porttitor turpis eget tellus rutrum faucibus Proin nisl mi ultricies non augue non malesuada porttitor erat Integer turpis elit luctus sed semper sed condimentum sed orci Mauris vel neque ac arcu mollis blandit non ut felis Integer justo dui lacinia ac aliquam in feugiat quis nisl Donec tempus orci vel velit ultrices tincidunt eget ac purus Mauris iaculis ipsum ac nisi placerat eu viverra sapien sollicitudin Vivamus scelerisque sagittis dolor a commodo massa auctor non Fusce nec volutpat ipsum Nullam luctus neque at est auctor nec convallis dui facilisis Aenean non eros mi Nullam ligula dui consectetur at quam in gravida fringilla lacus Vivamus pulvinar dignissim justo vel finibus leo egestas id Vestibulum tincidunt varius sem sit amet volutpat enim feugiat a Maecenas eget rutrum lorem Nulla facilisis velit non efficitur sodales erat nulla vulputate risus nec varius ligula turpis ut quam Aliquam erat volutpat Maecenas pulvinar ac quam eu condimentum Proin pulvinar luctus massa et faucibus Integer ullamcorper nibh ac quam facilisis vestibulum Pellentesque et tellus eros Proin porttitor lorem ut nulla gravida vestibulum Donec at lorem et velit rhoncus aliquam sed tempor odio cras amet."

        expected = [
            "Nullam nec egestas purus Aliquam tincidunt in enim nec egestas Donec eget nunc vitae turpis mollis ultricies in vitae turpis Proin porttitor turpis eget tellus rutrum faucibus Proin nisl mi ultricies non augue non malesuada porttitor erat Integer turpis elit luctus sed semper sed condimentum sed orci Mauris vel neque ac arcu mollis blandit non ut felis Integer justo dui lacinia ac aliquam in feugiat quis nisl Donec tempus orci vel velit ultrices tincidunt eget ac purus Mauris iaculis ipsum ac nisi placerat eu viverra sapien sollicitudin Vivamus scelerisque sagittis dolor a commodo massa auctor non Fusce nec volutpat ipsum Nullam luctus neque at est auctor nec convallis dui facilisis Aenean non eros mi Nullam ligula dui consectetur at quam in gravida fringilla lacus Vivamus pulvinar dignissim justo vel finibus leo egestas id Vestibulum tincidunt varius sem sit amet volutpat enim feugiat a Maecenas eget rutrum lorem Nulla facilisis velit non efficitur sodales erat nulla vulputate risus", 
            " nec varius ligula turpis ut quam Aliquam erat volutpat Maecenas pulvinar ac quam eu condimentum Proin pulvinar luctus massa et faucibus Integer ullamcorper nibh ac quam facilisis vestibulum Pellentesque et tellus eros Proin porttitor lorem ut nulla gravida vestibulum Donec at lorem et velit rhoncus aliquam sed tempor odio cras amet."
        ]

        result = split_paragraph(long_sentence_no_punc)
        self.assertEqual(result, expected, msg=result)

        # make sure the function recurses as expected
        extra_long_sentence_no_punc = "Nullam nec egestas purus Aliquam tincidunt in enim nec egestas Donec eget nunc vitae turpis mollis ultricies in vitae turpis Proin porttitor turpis eget tellus rutrum faucibus Proin nisl mi ultricies non augue non malesuada porttitor erat Integer turpis elit luctus sed semper sed condimentum sed orci Mauris vel neque ac arcu mollis blandit non ut felis Integer justo dui lacinia ac aliquam in feugiat quis nisl Donec tempus orci vel velit ultrices tincidunt eget ac purus Mauris iaculis ipsum ac nisi placerat eu viverra sapien sollicitudin Vivamus scelerisque sagittis dolor a commodo massa auctor non Fusce nec volutpat ipsum Nullam luctus neque at est auctor nec convallis dui facilisis Aenean non eros mi Nullam ligula dui consectetur at quam in gravida fringilla lacus Vivamus pulvinar dignissim justo vel finibus leo egestas id Vestibulum tincidunt varius sem sit amet volutpat enim feugiat a Maecenas eget rutrum lorem Nulla facilisis velit non efficitur sodales erat nulla vulputate risus nec varius ligula turpis ut quam Aliquam erat volutpat Maecenas pulvinar ac quam eu condimentum Proin pulvinar luctus massa et faucibus Integer ullamcorper nibh ac quam facilisis vestibulum Pellentesque et tellus eros Proin porttitor lorem ut nulla gravida vestibulum Donec at lorem et velit rhoncus aliquam sed tempor odio cras amet Nullam nec egestas purus Aliquam tincidunt in enim nec egestas Donec eget nunc vitae turpis mollis ultricies in vitae turpis Proin porttitor turpis eget tellus rutrum faucibus Proin nisl mi ultricies non augue non malesuada porttitor erat Integer turpis elit luctus sed semper sed condimentum sed orci Mauris vel neque ac arcu mollis blandit non ut felis Integer justo dui lacinia ac aliquam in feugiat quis nisl Donec tempus orci vel velit ultrices tincidunt eget ac purus Mauris iaculis ipsum ac nisi placerat eu viverra sapien sollicitudin Vivamus scelerisque sagittis dolor a commodo massa auctor non Fusce nec volutpat ipsum Nullam luctus neque at est auctor nec convallis dui facilisis Aenean non eros mi Nullam ligula dui consectetur at quam in gravida fringilla lacus Vivamus pulvinar dignissim justo vel finibus leo egestas id Vestibulum tincidunt varius sem sit amet volutpat enim feugiat a Maecenas eget rutrum lorem Nulla facilisis velit non efficitur sodales erat nulla vulputate risus nec varius ligula turpis ut quam Aliquam erat volutpat Maecenas pulvinar ac quam eu condimentum Proin pulvinar luctus massa et faucibus Integer ullamcorper nibh ac quam facilisis vestibulum Pellentesque et tellus eros Proin porttitor lorem ut nulla gravida vestibulum Donec at lorem et velit rhoncus aliquam sed tempor odio cras amet."

        expected = [
            "Nullam nec egestas purus Aliquam tincidunt in enim nec egestas Donec eget nunc vitae turpis mollis ultricies in vitae turpis Proin porttitor turpis eget tellus rutrum faucibus Proin nisl mi ultricies non augue non malesuada porttitor erat Integer turpis elit luctus sed semper sed condimentum sed orci Mauris vel neque ac arcu mollis blandit non ut felis Integer justo dui lacinia ac aliquam in feugiat quis nisl Donec tempus orci vel velit ultrices tincidunt eget ac purus Mauris iaculis ipsum ac nisi placerat eu viverra sapien sollicitudin Vivamus scelerisque sagittis dolor a commodo massa auctor non Fusce nec volutpat ipsum Nullam luctus neque at est auctor nec convallis dui facilisis Aenean non eros mi Nullam ligula dui consectetur at quam in gravida fringilla lacus Vivamus pulvinar dignissim justo vel finibus leo egestas id Vestibulum tincidunt varius sem sit amet volutpat enim feugiat a Maecenas eget rutrum lorem Nulla facilisis velit non efficitur sodales erat nulla vulputate risus", 
            " nec varius ligula turpis ut quam Aliquam erat volutpat Maecenas pulvinar ac quam eu condimentum Proin pulvinar luctus massa et faucibus Integer ullamcorper nibh ac quam facilisis vestibulum Pellentesque et tellus eros Proin porttitor lorem ut nulla gravida vestibulum Donec at lorem et velit rhoncus aliquam sed tempor odio cras amet Nullam nec egestas purus Aliquam tincidunt in enim nec egestas Donec eget nunc vitae turpis mollis ultricies in vitae turpis Proin porttitor turpis eget tellus rutrum faucibus Proin nisl mi ultricies non augue non malesuada porttitor erat Integer turpis elit luctus sed semper sed condimentum sed orci Mauris vel neque ac arcu mollis blandit non ut felis Integer justo dui lacinia ac aliquam in feugiat quis nisl Donec tempus orci vel velit ultrices tincidunt eget ac purus Mauris iaculis ipsum ac nisi placerat eu viverra sapien sollicitudin Vivamus scelerisque sagittis dolor a commodo massa auctor non Fusce nec volutpat ipsum Nullam luctus neque at est auctor",
            " nec convallis dui facilisis Aenean non eros mi Nullam ligula dui consectetur at quam in gravida fringilla lacus Vivamus pulvinar dignissim justo vel finibus leo egestas id Vestibulum tincidunt varius sem sit amet volutpat enim feugiat a Maecenas eget rutrum lorem Nulla facilisis velit non efficitur sodales erat nulla vulputate risus nec varius ligula turpis ut quam Aliquam erat volutpat Maecenas pulvinar ac quam eu condimentum Proin pulvinar luctus massa et faucibus Integer ullamcorper nibh ac quam facilisis vestibulum Pellentesque et tellus eros Proin porttitor lorem ut nulla gravida vestibulum Donec at lorem et velit rhoncus aliquam sed tempor odio cras amet."
        ]

        result = split_paragraph(extra_long_sentence_no_punc)
        self.assertEqual(result, expected, msg=result)


def compare_metadata(dict_metadata, other_metadata):
    """Compare a list of ``Property`` objects to a ``dict``.

    Parameters:
        dict_metadata (dict): A dict to check other_metadata against, like
            self.metadata.
        other_metadata (list of Propertys): The ``Property``\s to check.

    Returns:
        boolean: ``True`` if every item in the ``dict`` is represented in
        ``other_metadata``, with values corresponding to ``Property.value``\s
        and values corresponding to ``Property.name``\s. ``False`` if not.
    """
    unique_data = []
    for datum in other_metadata:
        unique_data.append(datum.name)

        if datum.name not in dict_metadata.keys():
            print "Property " + datum.name + " not in self.meta"
            return False

        if datum.value not in dict_metadata[datum.name]:
            print "Value " + datum.value + " not accepted for property " +\
                datum.name
            return False

    if len(list(set(unique_data))) != len(dict_metadata):
        print "Lengths of sets not equal"
        return False

    return True

