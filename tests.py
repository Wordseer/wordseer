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

if __name__ == '__main__':
    unittest.main()
