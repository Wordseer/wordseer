"""Tests for the StringProcessor.
"""
import mock
import unittest

from app.models.sentence import Sentence
from app.models.dependency import Dependency
from app.models.project import Project
from app.preprocessor import stringprocessor
import database
import pdb
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
        self.result = t.tokenize(self.example)
        self.raw = t.parser.raw_parse(self.example)

    def test_text(self):
        """Test to make sure the text is accurately transscribed.
        """
        for s in range(0, len(self.result)):
            for w in range(0, len(self.result[s].words)):
                word = self.result[s].words[w]
                raw_word = self.raw["sentences"][s]["words"][w]
                assert word.lemma == raw_word[1]["Lemma"].lower()

    def test_tags(self):
        """Test to make sure the words are accurately tagged.
        """
        # Make sure the words are tagged.
        for sentence in self.result:
            for word in sentence.word_in_sentence:
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

    def test_sentences(self):
        """Make sure it's a list of the given sentence.
        """
        self.failUnless(len(self.result) == 1)
        self.failUnless(isinstance(self.result[0], Sentence))
        self.failUnless(self.result[0].text == self.example)

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

@mock.patch.object(stringprocessor, "tokenize_from_raw")
@mock.patch("app.preprocessor.stringprocessor.StanfordCoreNLP.raw_parse")
class ParseTests(unittest.TestCase):
    """Tests for the parse() method.
    """

    def setUp(self):
        """Mock out the parser for testing.
        """
        database.clean()
        #t.parser = mock.MagicMock()

    @mock.patch("app.preprocessor.stringprocessor.Word.query", autospec=True)
    @mock.patch("app.preprocessor.stringprocessor.Dependency.query", autospec=True)
    def test_parse(self, mock_dependency_query, mock_word_query, mock_parser, mock_tokenizer):
        """Test the parse method.
        """
        sent = mock.create_autospec(Sentence, text="The fox is brown.")
        parsed_dict = {"sentences":
            [
                {'dependencies':
                    [('det', 'fox', '2', 'The', '1'),
                    ('nsubj', 'brown', '4', 'fox', '2'),
                    ('cop', 'brown', '4', 'was', '3'),
                    ('root', 'ROOT', '0', 'brown', '4')],
                "words": mock.MagicMock(name="WordsDict"),
                "parsetree": mock.MagicMock(name="parsetree")
                }
            ]
        }

        deps = parsed_dict["sentences"][0]["dependencies"]
        words = parsed_dict["sentences"][0]["words"]
        parsetree = parsed_dict["sentences"][0]["parsetree"]

        # Set up our mock parse result dict
        mock_result = mock.MagicMock(spec_set=dict, name="Dict")
        mock_result.__getitem__.side_effect = parsed_dict.__getitem__
        mock_result.__setitem__.side_effect = parsed_dict.__setitem__
        mock_parser.return_value = mock_result

        # Run the method
        result = t.parse(sent, {}, {})

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

    @mock.patch("app.preprocessor.stringprocessor.project_logger", autospec=True)
    def test_parse_twosentences(self, mock_logger, mock_parser, mock_tokenizer):
        """Check to make sure that parse() will log a warning on multiple
        sentences.
        """

        sent = Sentence(text="The fox is brown.")
        parsed_dict = {"sentences": [mock.MagicMock(name="Sentence1"),
            mock.MagicMock(name="Sentence2")]}

        mock_result = mock.MagicMock(spec_set=dict, name="Dict")
        mock_result.__getitem__.side_effect = parsed_dict.__getitem__
        mock_result.__setitem__.side_effect = parsed_dict.__setitem__
        mock_parser.return_value = mock_result

        t.parse(sent)
        mock_logger.warning.assert_called_with("More than one sentence passed "
            "in to StringProcessor.parse().")

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

