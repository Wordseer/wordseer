import unittest
from structureextractor import StructureExtractor
import tokenizer

class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.structure_file = "tests/data/structure.json"
        self.input_file = open("tests/data/articles/post1.xml")
        t = tokenizer.Tokenizer()
        self.extractor = StructureExtractor(t, self.structure_file)

    @unittest.skip("Depends on extract_unit_information()")
    def test_extract(self):
        documents = self.extractor.extract(self.input_file)

    @unittest.skip("Root selector problems")
    def test_extract_unit_information(self):
        pass

    def test_css_maker(self):
        xpaths = {"./author/text()": ":root > author ",
            "./title/text()": ":root > title ",
            "./time/text()": ":root > time ",
            "./number/text()": ":root > number ",
            "./tags/tag/text()": ":root > tags > tag "}
        for path, selector in xpaths.items():
            self.failUnless(selector == self.extractor.make_css_selector(path))

    @unittest.skip("Root selector problems")
    def test_get_sentences(self):
        pass

    @unittest.skip("Depends on get_xpath_attribute")
    def test_get_metadata(self):
        pass

    @unittest.skip("Root selector problems")
    def test_get_xpath_attribute(self):
        pass

    @unittest.skip("Root selector problems")
    def test_get_xpath_text(self):
        pass

def main():
    unittest.main()

if __name__ == "__main__":
    main()