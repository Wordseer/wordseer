"""
Unit tests for the components of the wordseer web interface.
"""

from cStringIO import StringIO
import os
import tempfile
import unittest

import mock
from sqlalchemy import create_engine

from app import app, database
from app.models import *

app.testing = True

def reset_db():
    open(app.config["SQLALCHEMY_DATABASE_PATH"], 'w').close()
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Base.metadata.create_all(engine)

class TestModels(unittest.TestCase):
    def setUp(self):
        reset_db()

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

        retrieved_prop = Property.filter(Property.name=="title").\
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

        retrieved_prop = Property.filter(name=="title").\
            filter(value == "Hello World").first()

        assert retrieved_prop.name == prop.name
        assert retrieved_prop.value == prop.value

class ViewsTests(unittest.TestCase):
    def setUp(self):
        """Clear the database for the next unit test.
        """
        self.client = app.test_client()
        reset_db()

    def test_no_projects(self):
        """Test the projects view with no projects present.
        """
        result = self.client.get("/projects/")
        assert "no projects" in result.data

    def test_projects(self):
        """Test the projects view with a project present.
        """
        new_project = Project(name="test")
        new_project.save()
        result = self.client.get("/projects/")
        assert "/projects/1" in result.data

    def test_projects_empty_post(self):
        """Test POSTing without a project name to the projects view.
        """
        result = self.client.post("/projects/")
        assert "no projects" in result.data
        assert "This field is required" in result.data

    @mock.patch("app.views.os", autospec=os)
    def test_projects_valid_post(self, mock_os):
        """Test POSTing with a valid project name.

        The view should have the name and the path to the project.
        """
        mock_os.path.join.return_value = "test_path"
        
        result = self.client.post("/projects/", data={
            "create-submitted": "true",
            "create-name": "test project"})

        assert "test project" in result.data
        assert "/projects/1" in result.data

    @unittest.skip("not quite working")
    def test_document_show(self):
        """Test the detail document view.
        """
        project = Project(name="test project", path="/test-path/")
        project.save()

        document = Unit(path="/test-path/test-file.xml", project=project)
        document.save()

        result = self.client.get("/projects/1/documents/1")

        assert "/uploads/" + str(document.id) in result
        assert "test-file.xml" in result

    @unittest.skip("requires research")
    def test_projects_post(self):
        upload_dir = tempfile.mkdtemp()
        app.config["UPLOAD_DIR"] = upload_dir
        result = self.client.post("/projects/", data=dict(
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
