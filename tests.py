import os
import unittest

from app.models import *
from database import prep_test

class TestCase(unittest.TestCase):
    def setUp(self):
        prep_test()

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
        print("word.sentences", w1.sentences)
        print("unit.sentences", u1.sentences)
        print("unit.properties", u1.properties)

        # Try saving all models
        models = [w1, w2, s1, u1, p1]
        [ model.save() for model in models ]

        # Try querying for the models again
        p2 = Property.query.filter(Property.name=='title' and Property.value=='Hello World').first()
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

        # Make a document
        d1 = Document("test", "path/to/d1")
        d1.save()

        print("New document", str(d1))
        print("Document unit", str(d1.unit))

        # Add units to the document
        d1.children.append(u1)
        d1.save()

        print("Children of d1", str(d1.children))
        print("Parent of u1", str(u1.parent.document))


    """
    #######
    Helpers
    #######
    """

if __name__ == '__main__':
    unittest.main()
