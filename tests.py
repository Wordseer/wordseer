import os
import unittest

from app.models import *

#TODO: unit tests shouldn't rely on human checking of their output
#TODO: this outputs too much!

class TestWordseer(unittest.TestCase):
    def setUp(self):
        # TODO: figure out how to set up a test database
        pass

    def tearDown(self):
        pass

    def test_model_word(self):
        """Test to make sure that the atttributes of the Word model can be
        properly set.
        """

        string_1 = "hello"
        string_2 = "world"

        word_1 = Word()
        word_2 = Word()

        word_1.word = string_1
        word_2.word = string_2

        assert word_1.word == string_1
        assert word_2.word == string_2

        word_1.save()
        word_2.save()

    def test_model_sentence(self):
        """Test to make sure that Sentence is working properly.
        """

        text = "hello world"
        sentence = Sentence()
        sentence.text = text

        assert sentence.text == text

        word_1 = Word(word="hello")
        word_2 = Word(word="world")

        sentence.words.append(word_1)
        sentence.words.append(word_2)

        assert sentence.words == [word_1, word_2]

        sentence.save()

    def test_model_unit(self):
        """Test to make sure that Unit is working properly.
        """

        unit_type = "section"
        number = 1

        unit = Unit()

        unit.unit_type = unit_type
        unit.number = number

        assert unit.unit_type == unit_type
        assert unit.number == number

        sentence = Sentence()
        sentence.words = [Word(word="hello"), Word(word="world")]
        prop = Property(name="title", value="Hello World")

        unit.sentences.append(sentence)
        unit.properties.append(prop)

        assert unit.sentences == [sentence]
        assert unit.properties == [prop]

        unit.save()

        retrieved_prop = session.query(Property).filter(name=="title").\
            filter(value == "Hello World").first()
        assert retrieved_prop.unit == unit

    def test_model_property(self):
        """Test ot make sure that Property is working properly.
        """

        prop = Property()

        name = "title"
        value = "Hello World"

        prop.name = name
        prop.value = value

        assert prop.name == name
        assert prop.value == value

        prop.save()

        retrieved_prop = session.query(Property).filter(name=="title").\
            filter(value == "Hello World").first()

        assert retrieved_prop == prop

    def test_sample_document(self):
        """Test turning a document file into the corresponding models.

        Once a document has been imported as an object, it should use the
        Unit constructor to initialize and save all models for the document.
        """
        #TODO: this doesn't test anything
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
                        doc_dict["properties"][words[0][:-1]] = " ".join(
                            words[1:])
                    else:
                        doc_dict["sentences"].append((line, words))
                else:
                    # Empty line
                    doc_dict["sentences"].append(("", ["\n"]))

        print(doc_dict)
        return doc_dict

if __name__ == '__main__':
    unittest.main()
