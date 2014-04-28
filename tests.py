import os
import unittest

from app.models import *

class TestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic_model(self):
        """Basic sanity test to make sure nothing major has broken.
        """

        # Try creating an instance of all models
        w1 = Word()
        w2 = Word()
        s1 = Sentence()
        u1 = Unit()
        p1 = Property()

        # Set attributes
        w1.word = "hello"
        w2.word = "world"

        s1.text = "hello world"

        u1.unit_type = "section"
        u1.number = 1

        p1.name = "title"
        p1.value = "Hello World"

        print("Words", w1.word, w2.word)
        print("Sentence", s1.text)
        print("Unit", u1.unit_type, u1.number)
        print("Property", p1.name, p1.value)

        # Try relationships
        s1.words.append(w1)
        s1.words.append(w2)

        u1.sentences.append(s1)

        u1.properties.append(p1)

        print("sentence.words", s1.words)
        print("unit.sentences", u1.sentences)
        print("unit.properties", u1.properties)

        # Try saving all models
        models = [w1, w2, s1, u1, p1]
        [ model.save() for model in models ]

        # Try querying for the models again
        p2 = Property.filter(Property.name=='title' and Property.value=='Hello World').first()
        u2 = p2.unit

        print("\"Hello World\" unit: ", u2.sentences)

        # Add a child to the unit
        u3 = Unit()
        u3.unit_type = "subsection"
        u3.number = 1

        p2 = Property()
        p2.name = "title"
        p2.value = "Foobar"

        u3.properties.append(p2)

        u1.children.append(u3)

        u3.save()
        u1.save()

        print("Children of u1", u1.children)
        print("u3's parent", u3.parent)

    def test_sample_document(self):
        """Test turning a document file into the corresponding models.

        Once a document has been imported as an object, it should use the
        Unit constructor to initialize and save all models for the document.
        """

        # Import the document.
        document = self.import_document("sample_document.txt")
        doc_unit = Unit(document)

        # Look at document contents
        print(doc_unit.sentences)

    """
    #######
    Helpers
    #######
    """

    def import_document(self, filename):
        """Simulate a document import without using a processor.
        """

        doc_dict = dict()
        doc_dict["subunits"] = dict()
        doc_dict["properties"] = dict()
        doc_dict["sentences"] = list()

        with open(filename) as document:
            for line in document:
                words = line.split()

                if words:
                    if words[0][-1] == ":":
                        doc_dict["properties"][words[0][:-1]] = " ".join(words[1:])
                    else:
                        doc_dict["sentences"].append((line, words))
                else:
                    # Empty line
                    doc_dict["sentences"].append(("", ["\n"]))

        print(doc_dict)
        return doc_dict

if __name__ == '__main__':
    unittest.main()
