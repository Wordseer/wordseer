import unittest
from structureextractor import *
import tokenizer
from lxml import etree

class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.structure_file = "tests/data/structure.json"
        self.input_file = "tests/data/articles/post1.xml"
        t = tokenizer.Tokenizer()
        self.extractor = StructureExtractor(t, self.structure_file)

    @unittest.skip("Depends on extract_unit_information()")
    def test_extract(self):
        with open(self.input_file) as f:
            documents = self.extractor.extract(f)

    @unittest.skip("Root selector problems")
    def test_extract_unit_information(self):
        pass

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

    def test_get_nodes_from_xpath(self):
        with open(self.input_file) as f:
            tree = etree.parse(f)
        root = tree.getroot()
        xpaths = {"./author/text()": root[2],
            "./title/text()": root[1],
            "./time/text()": root[0],
            "./number/text()": root[4],
            "./tags/tag/text()": root[3],
            "   ": root}

        for xpath, result in xpaths.items():
            print result
            print get_nodes_from_xpath(xpath, root)
            self.failUnless(result == get_nodes_from_xpath(xpath, tree))

def main():
    unittest.main()

if __name__ == "__main__":
    main()