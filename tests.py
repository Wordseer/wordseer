"""
Unit tests for the components of the wordseer web interface.
"""

from cStringIO import StringIO
import os
import tempfile
import unittest

from app import app

class TestModels(unittest.TestCase):
    def setUp(self):
        """Set up the database for the models tests.
        """
        Base.environment = 'test'

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
        prop.save()

        retrieved_prop = session.query(Property).\
            filter(Property.name=="title").\
            filter(Property.value == "Hello World").first()

        assert retrieved_prop.unit.unit_type == unit.unit_type
        assert retrieved_prop.unit.number == unit.number

    def test_model_property(self):
        """Test to make sure that Property is working properly.
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

        assert retrieved_prop.name == prop.name
        assert retrieved_prop.value == prop.value

class ViewsTests(unittest.TestCase):
    def setUp(self):
        """Clear the database for the next unit test.
        """
        # TODO: this is awful, hopefully flask.ext.sqlalchemy will save us
        tmp_db.truncate(0)
        engine = create_engine("sqlite:///" + tmp_db.name)
        Base.metadata.create_all(engine)

    def test_no_projects(self):
        """Test the projects view with no projects present.
        """
        result = client.get("/projects/")
        assert "no projects" in result.data

    def test_projects(self):
        """Test the projects view with a project present.
        """
        new_project = Project(name="test")
        new_project.save()
        result = client.get("/projects/")
        assert "/projects/1" in result.data

    def test_projects_empty_post(self):
        """Test POSTing without a file to the projects view.
        """
        result = client.post("/projects/")
        assert "no projects" in result.data

    def test_projects_post(self):
        upload_dir = tempfile.mkdtemp()
        app.config["UPLOAD_DIR"] = upload_dir
        result = client.post("/projects/", data=dict(
            upload_var=(StringIO("Test file"), "test.xml")))
        uploaded_file = open(os.path.join(upload_dir, "test.xml"))

@unittest.skip("Should be rewritten to use David's code.")
class ImportTests(unittest.TestCase):
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
