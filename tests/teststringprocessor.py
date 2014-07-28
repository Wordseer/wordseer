"""Tests for the StringProcessor.
"""
import mock
import unittest

from app.models.sentence import Sentence
from app.models.dependency import Dependency
from app.models.parseproducts import ParseProducts
from lib.wordseerbackend.wordseerbackend import stringprocessor

t = stringprocessor.StringProcessor()

class CommonTests(object):
    """Tests and variables common to several test cases.
    """
    def setUp(self, text=""):
        """Set up some local variables.
        """
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
                assert word.word == raw_word[0]
                assert word.lemma == raw_word[1]["Lemma"]
                assert word.part_of_speech == raw_word[1]["PartOfSpeech"]

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
    def setUp(self):
        """Set up the local variables.
        """
        example = ("She should have died hereafter; There would have "
            "been a time for such a word. Tomorrow, and tomorrow, and "
            "tomorrow, Creeps in this petty pace from day to day, To the "
            "last syllable of recorded time; And all our yesterdays have "
            "lighted fools The way to dusty death. Out, out, brief candle! "
            "Life's but a walking shadow, a poor player That struts and "
            "frets his hour upon the stage And then is heard no more. It "
            "is a tale Told by an idiot, full of sound and fury Signifying "
            "nothing.")
        super(TokenizeParagraphTests, self).setUp(text=example)

    def test_sentences(self):
        """Make sure it's a list of all the sentences.
        """
        # Todo: Check without hardcoding the ends?
        for sent in self.result:
            self.failUnless(isinstance(sent, Sentence))
            self.failUnless(sent.words[-2].word in ["word", "death",
                "candle", "more", "nothing"])

class TokenizeSentenceTests(CommonTests, unittest.TestCase):
    """Test tokenize() given a single sentence.
    """
    def setUp(self):
        """Set up the example text.
        """
        example = "The quick brown fox jumped over the lazy dog."
        super(TokenizeSentenceTests, self).setUp(text=example)

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
@mock.patch("lib.wordseerbackend.wordseerbackend.stringprocessor.StanfordCoreNLP.raw_parse")
class ParseTests(unittest.TestCase):
    """Tests for the parse() method.
    """

    def setUp(self):
        """Mock out the parser for testing.
        """
        #t.parser = mock.MagicMock()

    @mock.patch("lib.wordseerbackend.wordseerbackend.stringprocessor.Word.query", autospec=True)
    @mock.patch("lib.wordseerbackend.wordseerbackend.stringprocessor.Dependency.query", autospec=True)
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
            expected_added_deps.append(mock.call(
                dependency=mock_dependency_query.filter_by.return_value.one.return_value,
                governor_index=gov_index,
                dependent_index=dep_index))

        sent.add_dependency.assert_has_calls(expected_added_deps)

    def test_parse_twosentences(self, mock_parser, mock_tokenizer):
        """Check to make sure that parse() will only parse a single sentence.
        """

        sent = Sentence(text="The fox is brown.")
        parsed_dict = {"sentences": [mock.MagicMock(name="Sentence1"),
            mock.MagicMock(name="Sentence2")]}

        mock_result = mock.MagicMock(spec_set=dict, name="Dict")
        mock_result.__getitem__.side_effect = parsed_dict.__getitem__
        mock_result.__setitem__.side_effect = parsed_dict.__setitem__
        mock_parser.return_value = mock_result

        self.assertRaises(ValueError, t.parse, sent)

    @unittest.skip("Feature in limbo")
    def test_parse_maxlength(self, mock_parser, mock_tokenizer):
        """Check to make sure that parse() uses a rudimentary sentence length
        check.
        """

        sent = mock.MagicMock(name="sentence")

        sent.split.return_value = range(0, 60)

        self.assertRaises(ValueError, t.parse, sent)

