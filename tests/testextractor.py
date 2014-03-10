import unittest
import structureextractor
import tokenizer

#@unittest.skip("Not yet working")
class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.structure_file = "tests/data/structure.json"
        self.input_file = open("tests/data/articles/post1.xml")
        t = tokenizer.Tokenizer()
        extractor = structurextractor.StructureExtractor(t, structure_file)
        documents = extractor.extract(self.input_file)

    def test_css_maker(self):
        xpaths = {"./author/text()": ":root > author > ",
            "./title/text()": ":root > title > ",
            "./time/text()": ":root > time > ",
            "./number/text()": ":root > number > ",
            "./tags/tag/text()": ":root > tags > tag > "}
        for path, selector in xpaths.items():
            self.failunless(selector == extractor.make_css_selector(path))

def main():
    unittest.main()

if __name__ == "__main__":
    main()