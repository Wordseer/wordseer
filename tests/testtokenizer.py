import unittest
import tokenizer

class TokenizerTests(unittest.TestCase):
    def test_init(self):
        t = tokenizer.Tokenizer()
        self.failUnless(t)

def main():
    unittest.main()

if __name__ == "__main__":
    main()