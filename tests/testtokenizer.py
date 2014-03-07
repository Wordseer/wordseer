import unittest
import tokenizer
from document import sentence

class TokenizerTests(unittest.TestCase):
    def test_init(self):
        t = tokenizer.Tokenizer()
        self.failUnless(t)

class SentenceTests(unittest.TestCase):
    def setUp(self):
        sent = "The quick brown fox jumped over the lazy dog."
        t = tokenizer.Tokenizer()
        self.result = t.tokenize(sent)
        
    def test_sentences(self):
        # Make sure it's a list of sentences.
        s = sentence.Sentence()
        for sent in self.result: 
            self.failUnless(isinstance(sent, sentence.Sentence))

def main():
    unittest.main()

if __name__ == "__main__":
    main()