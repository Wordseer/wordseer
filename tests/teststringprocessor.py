"""Tests for the StringProcessor.
"""
import mock
import unittest
import json
from lxml import etree
import pdb

from app.models.sentence import Sentence
from app.models.dependency import Dependency
from app.models.project import Project
from app.models.documentfile import DocumentFile 
from app.models.association_objects import WordInSentence

from app.preprocessor import stringprocessor
from app.preprocessor.structureextractor import *

import database

t = stringprocessor.StringProcessor(Project())

class CommonTests(object):
    """Tests and variables common to several test cases.
    """
    @classmethod
    def setUpClass(self, text=""):
        """Set up some local variables.
        """
        database.clean()
        t.project = Project()
        self.example = text
        # TODO: this method doesn't exist anymore, it was making
        # a redundant parser call
        # self.result = t.tokenize(self.example)
        self.raw = t.parser.raw_parse(self.example)

    @unittest.skip("self.result uses the outdated tokenize() method; need to rewrite")
    def test_text(self):
        """Test to make sure the text is accurately transscribed.
        """
        for s in range(0, len(self.result)):
            for w in range(0, len(self.result[s].words)):
                word = self.result[s].words[w]
                raw_word = self.raw["sentences"][s]["words"][w]
                assert word.lemma == raw_word[1]["Lemma"].lower()

    @unittest.skip("self.result uses the outdated tokenize() method; need to rewrite")
    def test_tags(self):
        """Test to make sure the words are accurately tagged.
        """
        # Make sure the words are tagged.
        for sentence in self.result:
            for word in sentence.words:
                self.failIf(word.part_of_speech == "")

class TokenizeParagraphTests(CommonTests, unittest.TestCase):
    """Test tokenize() using a paragraph of text.
    """
    @classmethod
    def setUpClass(self):
        """Set up the local variables.
        """
        example = ("She should have died hereafter; There would have "
            "been a time for such a word. Tomorrow, and tomorrow, and "
            "tomorrow, Creeps in this petty pace from day to day, To the "
            "last syllable of recorded time; And all our yesterdays have "
            "lighted fools The way to dusty death. Out, out, brief candle! ")
        super(TokenizeParagraphTests, self).setUpClass(text=example)

    @unittest.skip("self.result uses the outdated tokenize() method; need to rewrite")
    def test_sentences(self):
        """Make sure it's a list of all the sentences.
        """
        # Todo: Check without hardcoding the ends?
        for sent in self.result:
            self.failUnless(isinstance(sent, Sentence))
            self.failUnless(sent.words[-2].lemma in ["word", "death",
                "candle"])

class TokenizeSentenceTests(CommonTests, unittest.TestCase):
    """Test tokenize() given a single sentence.
    """
    @classmethod
    def setUpClass(self):
        """Set up the example text.
        """
        example = "The quick brown fox jumped over the lazy dog."
        super(TokenizeSentenceTests, self).setUpClass(text=example)

    @unittest.skip("self.result uses the outdated tokenize() method; need to rewrite")
    def test_sentences(self):
        """Make sure it's a list of the given sentence.
        """
        self.failUnless(len(self.result) == 1)
        self.failUnless(isinstance(self.result[0], Sentence))
        self.failUnless(self.result[0].text == self.example)

    @unittest.skip("self.result uses the outdated tokenize() method; need to rewrite")
    def test_space_before(self):
        """Make sure space_before has been properly done
        """
        for s in range(0, len(self.result)):
            for w in range(0, len(self.result[s].word_in_sentence)):
                space = self.result[s].word_in_sentence[w].space_before

                try:
                    actual_char = self.example[int(self.raw["sentences"][s]\
                        ["words"][w][1]["CharacterOffsetBegin"]) - 1]
                except IndexError:
                    actual_char = " "

                if actual_char == " ":
                    assert space == " "
                else:
                    assert space == ""

@mock.patch("app.preprocessor.stringprocessor.StanfordCoreNLP.raw_parse")
class ParseTests(unittest.TestCase):
    """Tests for the parse() method.
    """

    def setUp(self):
        """Mock out the parser for testing.
        """
        database.clean()
        #t.parser = mock.MagicMock()

    @unittest.skip("This parser works very different now; test needs to be rewritten")
    @mock.patch("app.preprocessor.stringprocessor.Word.query", autospec=True)
    @mock.patch("app.preprocessor.stringprocessor.Dependency.query", autospec=True)
    def test_parse(self, mock_dependency_query, mock_word_query, mock_parser):
        """Test the parse method.
        """
        sent = mock.create_autospec(Sentence, text="The fox is brown.")
        text = "The fox is brown."
        parsed_dict = {"sentences":
            [
                {'dependencies':
                    [('det', 'fox', '2', 'The', '1'),
                    ('nsubj', 'brown', '4', 'fox', '2'),
                    ('cop', 'brown', '4', 'was', '3'),
                    ('root', 'ROOT', '0', 'brown', '4')],
                "words": mock.MagicMock(name="WordsDict"),
                }
            ]
        }

        deps = parsed_dict["sentences"][0]["dependencies"]
        words = parsed_dict["sentences"][0]["words"]

        # Set up our mock parse result dict
        mock_result = mock.MagicMock(spec_set=dict, name="Dict")
        mock_result.__getitem__.side_effect = parsed_dict.__getitem__
        mock_result.__setitem__.side_effect = parsed_dict.__setitem__
        mock_parser.return_value = mock_result

        # Run the method
        result = t.parse(text, {}, {})

        # The result should not contain the dependency containing ROOT
        expected_added_deps = []
        for dep in deps[0:3]:
            dep_index = int(dep[4]) - 1
            gov_index = int(dep[2]) - 1
            expected_added_deps.append(mock.call(project=t.project,
                dependency=mock_dependency_query.filter_by.return_value.one.return_value,
                governor_index=gov_index,
                dependent_index=dep_index,
                force=False))

        sent.add_dependency.assert_has_calls(expected_added_deps)

class ParseWithErrorHandlingTest(unittest.TestCase):
    """Test the parse_with_error_handling method.
    """

    def test_sanity(self):
        """Method should output the same result as running raw_parse directly
        when run on a normal sentence text.
        """
        database.clean()
        text = "The fox is brown."
        result = t.parse_with_error_handling(text)
        expected_result = t.parser.raw_parse(text)

        self.failUnless(result == expected_result)

class LongSentenceTests(unittest.TestCase):
    def setUp(self):
        """Parse the brief example"""
        database.clean()
        self.path = "tests/data/long_sentences/"
        self.structure_file = self.path + "structure.json"
        self.input_file = self.path + "document.xml"

        self.input_project = Project()
        t.project = self.input_project

        self.input_project.document_files.append(
            DocumentFile(path=self.input_file))
        self.input_project.save()

        with open(self.structure_file) as f:
            self.json = json.load(f)

        self.xml = etree.parse(self.input_file)
        self.extractor = StructureExtractor(self.input_project,
            self.structure_file, t)

    def test_long_sent_parsing(self):
        """test that long paragraphs are split and their spaces indexed properly by the parser
        """
        # run the parser
        self.extractor.extract(self.input_file)

        sentences = self.input_project.sentences
        
        # test short paragraph with normal sentences
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[0].id).all()
        self.assertEqual(words[2].surface, "a")
        self.assertEqual(words[2].space_before, " ")
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[1].id).all()
        self.assertEqual(words[2].surface, "the")
        self.assertEqual(words[2].space_before, " ")

        # test long paragraph with normal sentences
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[3].id).all()
        self.assertEqual(words[2].surface, "a")
        self.assertEqual(words[2].space_before, " ")
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[4].id).all()
        self.assertEqual(words[7].surface, "ipsum")
        self.assertEqual(words[7].space_before, " ")

        # test long sentence with punctuation
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[5].id).all()
        self.assertEqual(words[7].surface, "long")
        self.assertEqual(words[7].space_before, " ")
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[6].id).all()
        self.assertEqual(words[6].surface, "consectetur")
        self.assertEqual(words[6].space_before, " ")

        # test long sentence with no punctuation
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[8].id).all()
        self.assertEqual(words[3].surface, "hella")
        self.assertEqual(words[3].space_before, " ")
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[9].id).all()
        self.assertEqual(words[2].surface, "sodales")
        self.assertEqual(words[2].space_before, " ")

        # test no punctuation with recursion
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[10].id).all()
        self.assertEqual(words[3].surface, "even")
        self.assertEqual(words[3].space_before, " ")
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[11].id).all()
        self.assertEqual(words[1].surface, "facilisis")
        self.assertEqual(words[1].space_before, " ")
        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[12].id).all()
        self.assertEqual(words[2].surface, "Fusce")
        self.assertEqual(words[2].space_before, " ")


class LongSentencePlayTests(unittest.TestCase):
    def setUp(self):
        """Parse the brief example"""
        database.clean()
        self.path = "tests/data/plays/"
        self.structure_file = self.path + "structure.json"
        self.input_file = self.path + "brief_example.xml"

        self.input_project = Project()
        t.project = self.input_project

        self.input_project.document_files.append(
            DocumentFile(path=self.input_file))
        self.input_project.save()

        with open(self.structure_file) as f:
            self.json = json.load(f)

        self.xml = etree.parse(self.input_file)
        self.extractor = StructureExtractor(self.input_project,
            self.structure_file, t)

    def test_long_speech(self):
        """Test long sentences in combined paragraphs with line breaks
        """

        # run the parser
        self.extractor.extract(self.input_file)

        sentences = self.input_project.sentences

        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[4].id).all()
        self.assertEqual(words[3].surface, "forgeries")
        self.assertEqual(words[3].space_before, " ")
        self.assertEqual(words[7].surface, "And")
        self.assertEqual(words[7].space_before, "\n")

        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[5].id).all()
        self.assertEqual(words[10].surface, "As")
        self.assertEqual(words[10].space_before, "\n")
        self.assertEqual(words[11].surface, "in")
        self.assertEqual(words[11].space_before, " ")

        words = WordInSentence.query.filter(WordInSentence.sentence_id == sentences[6].id).all()
        self.assertEqual(words[4].surface, "land")
        self.assertEqual(words[4].space_before, " ")
        self.assertEqual(words[5].surface, "Have")
        self.assertEqual(words[5].space_before, "\n")

