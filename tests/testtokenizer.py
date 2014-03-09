import unittest
import tokenizer
from document import sentence

class CommonTests:
    @classmethod
    def setUpClass(commonTests, text=""):
            CommonTests.t = tokenizer.Tokenizer()

    def setUp(self, text=""):
            self.example = text
            self.result = self.t.tokenize(self.example)
            self.raw = self.t.parser.raw_parse(self.example)

    def test_text(self):
        for s in range(0, len(self.result)):
            for w in range(0, len(self.result[s].words)):
                self.failUnless(self.result[s].words[w] ==
                    self.raw["sentences"][s]["words"][w][0])

    def test_tags(self):
        # Make sure the words are tagged.
        for sent in self.result:
            for tw in sent.tagged:
                self.failIf(tw.tag == "")
        

class ParagraphTests(CommonTests, unittest.TestCase):
    def setUp(self):
        example = "She should have died hereafter; There would have " \
            + "been a time for such a word. Tomorrow, and tomorrow, and " \
            + "tomorrow, Creeps in this petty pace from day to day, To the " \
            + "last syllable of recorded time; And all our yesterdays have " \
            + "lighted fools The way to dusty death. Out, out, brief candle! " \
            + "Life's but a walking shadow, a poor player That struts and " \
            + "frets his hour upon the stage And then is heard no more. It " \
            + "is a tale Told by an idiot, full of sound and fury Signifying " \
            + "nothing."
        super(ParagraphTests, self).setUp(text = example)

    def test_sentences(self):
        # Make sure it's a list of all the sentences.
        # Todo: Check without hardcoding the ends?
        for sent in self.result: 
            self.failUnless(isinstance(sent, sentence.Sentence))
            self.failUnless(sent.tagged[-2].word[0] in ["word", "death",
                "candle", "more", "nothing"])

class SentenceTests(CommonTests, unittest.TestCase):
    def setUp(self):
        example = "The quick brown fox jumped over the lazy dog."
        super(SentenceTests, self).setUp(text = example)
        
    def test_sentences(self):
        # Make sure it's a list of sentences.
        for sent in self.result: 
            self.failUnless(isinstance(sent, sentence.Sentence))

    def test_space_before(self):
        # Make sure space_before has been properly done
        for s in range(0, len(self.result)):
            for w in range(0, len(self.result[s].words)):
                space = self.result[s].tagged[w].space_before
                actual_char = self.example[int(self.raw["sentences"][s]["words"]
                    [w][1]["CharacterOffsetBegin"])]
                if space == "":
                    self.failUnless(actual_char != " ")
                else:
                    self.failUnless(actual_char == " ")

def main():
    unittest.main()

if __name__ == "__main__":
    main()