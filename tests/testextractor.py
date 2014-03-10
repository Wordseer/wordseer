import unittest
import structureextractor
import tokenizer

@unittest.skip("Not yet working")
class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.structure_file = "data/occupy-collection-structure.json"
        self.input_file = \
            open("casestudies/occupy/xml/Houston__1__CBS Houston.xml")
        t = tokenizer.Tokenizer()
        extractor = structurextractor.StructureExtractor(t, structure_file)
        documents = extractor.extract(self.input_file)

    def test(self):
        self.failUnless(False)

def main():
    unittest.main()

if __name__ == "__main__":
    main()