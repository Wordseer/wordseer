import unittest
from structureextractor import StructureExtractor
import tokenizer

#@unittest.skip("JSON problems")
class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.structure_file = "tests/data/structure.json"
        self.input_file = open("tests/data/articles/post1.xml")
        t = tokenizer.Tokenizer()
        self.extractor = StructureExtractor(t, self.structure_file)

    def test_extractor(self):
        documents = self.extractor.extract(self.input_file)

    def test_css_maker(self):
        xpaths = {"./author/text()": ":root > author > ",
            "./title/text()": ":root > title > ",
            "./time/text()": ":root > time > ",
            "./number/text()": ":root > number > ",
            "./tags/tag/text()": ":root > tags > tag > "}
        for path, selector in xpaths.items():
            print(selector)
            print(self.extractor.make_css_selector(path))
            self.failUnless(selector == self.extractor.make_css_selector(path))

def main():
    unittest.main()

if __name__ == "__main__":
    main()