"""
Tests for the tokenizer.
"""

import mock
import unittest

#TODO: write parser tests
from document import sentence
import stringprocessor

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
                self.failUnless(self.result[s].words[w] ==
                    self.raw["sentences"][s]["words"][w][0])

    def test_tags(self):
        """Test to make sure the words are accurately tagged.
        """
        # Make sure the words are tagged.
        for sent in self.result:
            for tw in sent.tagged:
                self.failIf(tw.tag == "")

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
            self.failUnless(isinstance(sent, sentence.Sentence))
            self.failUnless(sent.tagged[-2].word[0] in ["word", "death",
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
        self.failUnless(isinstance(self.result[0], sentence.Sentence))
        self.failUnless(self.result[0].text == self.example)

    def test_space_before(self):
        """Make sure space_before has been properly done
        """
        for s in range(0, len(self.result)):
            for w in range(0, len(self.result[s].words)):
                space = self.result[s].tagged[w].space_before
                actual_char = self.example[int(self.raw["sentences"][s]["words"]
                    [w][1]["CharacterOffsetBegin"])]
                if space == "":
                    self.failUnless(actual_char != " ")
                else:
                    self.failUnless(actual_char == " ")

@mock.patch("stringprocessor.StanfordCoreNLP")
@mock.patch("stringprocessor.Dependency")
class ParseTests(unittest.TestCase):
    """Tests for the parse() method.
    """

    def setUp(self):
        """Mock out the parser for testing.
        """
        #t.parser = mock.MagicMock()

    def test_parse(self, mock_dep, mock_parser):
        """Test the parse method.
        """
        sentence = "The fox is brown."
        parsed_dict = {"sentences":
            [
                {'dependencies':
                    [('det', 'fox', '2', 'The', '1'),
                    ('nsubj', 'brown', '4', 'fox', '2'),
                    ('cop', 'brown', '4', 'was', '3'),
                    ('root', 'ROOT', '0', 'brown', '4')],
                'parsetree': ('(ROOT (S (NP (DT The) (NN fox)) (VP (VBZ is)'
                    ' (ADJP (JJ brown)))))')
                }
            ]
        }

        # Set up our mock parse result dict
        mock_result = mock.MagicMock(spec_set=dict)
        mock_result.__getitem__.side_effect = parsed_dict.__getitem__
        mock_result.__setitem__.side_effect = parsed_dict.__setitem__

        mock_parser.raw_parse.return_value = mock_result

        # Run the method
        t.parse(sentence)

        
