import unittest
from structureextractor import *
import tokenizer
import json
from lxml import etree

class CommonTests(object):
    #@classmethod
    #def setUpClass(commonTests):
    #    CommonTests.t = tokenizer.Tokenizer()

    def setUp(self, path, structure_file, input_file):
        self.structure_file = path + structure_file
        self.input_file = path + input_file
        with open(self.structure_file) as f:
            self.json = json.load(f)
        self.xml = etree.parse(self.input_file)
        t = tokenizer.Tokenizer()
        self.extractor = StructureExtractor(t, self.structure_file)

class PostTests(CommonTests, unittest.TestCase):
    def setUp(self):
        self.xpaths = ["./author/text()",
            "./title/text()",
            "./time/text()",
            "./number/text()",
            "./tags/tag/text()",
            "   "]
        super(PostTests, self).setUp(
            "tests/data/articles/", "structure.json", "post1.xml")

    @unittest.skip("Depends on extract_unit_information()")
    def test_extract(self):
        with open(self.input_file) as f:
            documents = self.extractor.extract(f)

    def test_extract_unit_information(self):
        self.failUnless(self.extractor.extract_unit_information(self.json,
            self.xml.getroot()) ==
            self.extractor.extract_unit_information(self.json, self.xml))
        #for unit in units:
        #    print unit
            
    def test_get_metadata(self):
        structure = self.json["metadata"]
        metadata = {"Time": "2012-02-23",
            "Author": "rachel",
            "Title": "Post 1",
            "Number": "1",
            "Tag": ["Tag 0", "Tag 3"]}
        results = get_metadata(structure, self.xml.getroot())
        for result in results:
            self.failUnless(result.property_name in metadata.keys())
            self.failUnless(result.value in metadata[result.property_name])

    @unittest.skip("Need example code")
    def test_get_xpath_attribute(self):
        pass
        
    def test_get_xpath_text(self):
        texts = [["rachel"],
            ["Post 1"],
            ["2012-02-23"],
            ["1"],
            ["Tag 0", "Tag 3"],
            ["\n2012-02-23\nPost 1\nrachel\n\n Tag 0\n Tag " +\
                "3\n\n1\n\n\tThis is the text of post 1. I love clouds.\n\n"]]
        key = dict(zip(self.xpaths, texts))
        for xpath, text in key.items():
            result = get_xpath_text(xpath, self.xml.getroot())
            self.failUnless(result == text)

class PlayTests(CommonTests, unittest.TestCase):
    def setUp(self):
        super(PlayTests, self).setUp(
            "tests/data/shakespeare/", "structure.json", "brief_example.xml")
        
    def test_get_sentences(self):
        #Test more cases?
        current_structure = self.json
        current_element = self.xml
        self.failUnless(self.extractor.get_sentences(self.json["units"][0],
            self.xml.getroot(), False)[0].sentence == etree.tostring(
            self.xml.getroot()[5], method="text").strip() + "\n")

def main():
    unittest.main()

if __name__ == "__main__":
    main()
