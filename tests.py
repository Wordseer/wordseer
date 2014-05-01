"""
Unit tests for the components of the wordseer web interface.
"""

from cStringIO import StringIO
import os
import shutil
import tempfile
import unittest

import mock
from sqlalchemy import create_engine

from app import app, db, user_datastore
from app.models import *

app.testing = True

def reset_db():
    open(app.config["SQLALCHEMY_DATABASE_PATH"], 'w').close()
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    db.Model.metadata.create_all(engine)

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

        retrieved_prop = Property.query.filter(Property.name=="title").\
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

        retrieved_prop = Property.query.filter(name=="title").\
            filter(value == "Hello World").first()

        assert retrieved_prop.name == prop.name
        assert retrieved_prop.value == prop.value

class ViewsTests(unittest.TestCase):
    def setUp(self):
        """Clear the database for the next unit test.
        """
        self.client = app.test_client()
        reset_db()
        user_datastore.create_user(email="foo@foo.com", password="password")
        db.session.commit()
        with self.client.session_transaction() as sess:
            sess["user_id"] = User.query.filter(User.id == 1).one().get_id()
            sess["_fresh"] = True

    def test_no_projects(self):
        """Test the projects view with no projects present.
        """
        result = self.client.get("/projects/")
        assert "no projects" in result.data

    def test_projects(self):
        """Test the projects view with a project present.
        """
        new_project = Project(name="test", user=1)
        new_project.save()
        result = self.client.get("/projects/")
        assert "/projects/1" in result.data

    def test_projects_bad_create(self):
        """Test creating an existing project.
        """
        project = Project(name="test", user=1)
        project.save()

        result = self.client.post("/projects/", data={
            "create-submitted": "true",
            "create-name": "test"
            })

        assert "already exists" in result.data

    def test_projects_empty_post(self):
        """Test POSTing without a project name to the projects view.
        """
        result = self.client.post("/projects/", data={
            "create-submitted": "true",
            "create-name": ""
            })
        
        assert "no projects" in result.data
        assert "You must provide a name" in result.data

    @mock.patch("app.views.os", autospec=os)
    def test_projects_valid_create_post(self, mock_os):
        """Test POSTing with a valid project name.

        The view should have the name and the path to the project.
        """
        mock_os.path.join.return_value = "test_path"
        
        result = self.client.post("/projects/", data={
            "create-submitted": "true",
            "create-name": "test project"
            })

        assert "test project" in result.data
        assert "/projects/1" in result.data

    @mock.patch("app.views.shutil", autospec=shutil)
    def test_projects_delete_post(self, mock_shutil):
        """Test project deletion.
        """

        project1 = Project(name="test1", path="/test-path/", user=1)
        project2 = Project(name="test2", path="/test-path/", user=1)
        project1.save()
        project2.save()

        result = self.client.post("/projects/", data={
            "action": "-1",
            "process-submitted": "true",
            "process-selection": ["1", "2"]
            })

        assert "no projects" in result.data
        mock_shutil.rmtree.assert_any_call(project1.path)
        mock_shutil.rmtree.assert_any_call(project2.path)
        assert mock_shutil.rmtree.call_count == 2

    def test_projects_bad_delete(self):
        """Test deleting without a selection.
        """

        project1 = Project(name="test1", user=1)
        project2 = Project(name="test2", user=1)
        project1.save()
        project2.save()

        result = self.client.post("/projects/", data={
            "action": "-1",
            "process-submitted": "true",
            })

        assert "must select" in result.data
        assert "/projects/1" in result.data
        assert "/projects/2" in result.data

    def test_projects_bad_process(self):
        """Test processing an unprocessable project.
        """

        project1 = Project(name="test1", user=1)
        project1.save()

        result = self.client.post("/projects/", data={
            "action": "0",
            "process-submitted": "true",
            "process-selection": ["1"]
            })

        assert "include exactly one json file" in result.data

    def test_projects_process(self):
        """Test processing a processable project.
        """
        project = Project(name="test", user=1)
        project.save()

        unit1 = Unit(project=project, path="/test-path/1.xml")
        unit2 = Unit(project=project, path="/test-path/2.json")
        unit1.save()
        unit2.save()

        result = self.client.post("/projects/", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1"]
            })

        assert "Errors have occurred" not in result.data

    def test_no_project_show(self):
        """Make sure project_show says that there are no files.
        """
        project = Project(name="test", user=1)
        project.save()
        result = self.client.get("/projects/1")

        assert "test" in result.data
        assert "There are no files in this project" in result.data

    def test_project_show(self):
        """Make sure project_show shows files.
        """
        project = Project(name="test", user=1)
        project.save()
        document1 = Unit(path="/test/doc1.xml", project=project)
        document2 = Unit(path="/test/doc2.xml", project=project)
        document1.save()
        document2.save()
        result = self.client.get("/projects/1")

        assert "doc1.xml" in result.data
        assert "doc2.xml" in result.data
        assert "/projects/1/documents/1" in result.data
        assert "/projects/1/documents/2" in result.data

    def test_project_show_upload(self):
        """Try uploading a file to the project_show view.
        """
        project = Project(name="test", user=1)
        project.save()
        
        upload_dir = tempfile.mkdtemp()
        app.config["UPLOAD_DIR"] = upload_dir
        os.makedirs(os.path.join(upload_dir, "1"))

        result = self.client.post("/projects/1", data={
            "upload-submitted": "true",
            "upload-uploaded_file": (StringIO("Test file"), "test.xml")
            })

        assert os.path.exists(os.path.join(upload_dir, "1", "test.xml"))
        assert "/projects/1/documents/1" in result.data
        assert "test.xml" in result.data

        uploaded_file = open(os.path.join(upload_dir, "1", "test.xml"))

        assert uploaded_file.read() == "Test file"

    def test_project_show_double_upload(self):
        """Try uploading two files with the same name to the project_show view.
        """
        project = Project(name="test", user=1)
        project.save()

        upload_dir = tempfile.mkdtemp()
        app.config["UPLOAD_DIR"] = upload_dir
        os.makedirs(os.path.join(upload_dir, "1"))

        self.client.post("/projects/1", data={
            "upload-submitted": "true",
            "upload-uploaded_file": (StringIO("Test file"), "test.xml")
            })

        result = self.client.post("/projects/1", data={
            "upload-submitted": "true",
            "upload-uploaded_file": (StringIO("Test file 2"), "test.xml")
            })

        assert "already exists" in result.data

    def test_project_show_no_post(self):
        """Try sending an empty post to project_show.
        """
        project = Project(name="test", user=1)
        project.save()

        result = self.client.post("/projects/1", data={
            "upload-submitted": "true"
            })

        assert "You must select a file" in result.data

        result = self.client.post("/projects/1", data={
            "process-submitted": "true"
            })

        assert "At least one document must be selected"

    @mock.patch("app.views.os", autospec=os)
    def test_project_show_delete(self, mock_os):
        """Test file deletion.
        """
        project = Project(name="test", user=1)
        project.save()

        unit1 = Unit(project=project, path="/test-path/1.xml")
        unit2 = Unit(project=project, path="/test-path/2.xml")
        unit1.save()
        unit2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "-1",
            "process-selection": ["1", "2"]
            })

        assert "no files in this project" in result.data
        mock_os.remove.assert_any_call(unit1.path)
        mock_os.remove.assert_any_call(unit2.path)
        assert mock_os.remove.call_count == 2

    def test_project_show_bad_delete(self):
        """Test a bad file delete request.
        """
        project = Project(name="test", user=1)
        project.save()

        unit1 = Unit(project=project, path="/test-path/1.xml")
        unit2 = Unit(project=project, path="/test-path/2.xml")
        unit1.save()
        unit2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "-1",
            })

        assert "must select" in result.data
        assert "/projects/1/documents/1" in result.data
        assert "/projects/1/documents/2" in result.data

    def test_project_show_process(self):
        """Test processing a processable group of files.
        """
        project = Project(name="test", user=1)
        project.save()

        unit1 = Unit(project=project, path="/test-path/1.xml")
        unit2 = Unit(project=project, path="/test-path/2.json")
        unit1.save()
        unit2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1", "2"]
            })

        assert "Errors have occurred" not in result.data

    def test_project_show_bad_process(self):
        """Test processing an unprocessable group of files.
        """
        project = Project(name="test", user=1)
        project.save()

        unit1 = Unit(project=project, path="/test-path/1.xml")
        unit2 = Unit(project=project, path="/test-path/2.xml")
        unit1.save()
        unit2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1", "2"]
            })

        assert "must include exactly one" in result.data

        unit1.path = "/test-path/1.json"
        unit1.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1"]
            })

        assert "At least one document must be selected" in result.data

    def test_document_show(self):
        """Test the detail document view.
        """
        project = Project(name="test project", path="/test-path/", user=1)
        project.save()

        document = Unit(path="/test-path/test-file.xml", project=project)
        document.save()

        result = self.client.get("/projects/1/documents/1")

        assert "/uploads/" + str(document.id) in result.data
        assert "test-file.xml" in result.data

    def test_get_file(self):
        """Run tests on the get_file view.
        """

        file_path = os.path.join(app.config["UPLOAD_DIR"], "upload_test.txt")

        project = Project(user=1)

        document = Unit(path=file_path, project=project)
        document.save()

        result = self.client.get("/uploads/1")

        with open(file_path) as test_file:
            assert result.data == test_file.read()

class AuthTests(unittest.TestCase):
    """Make sure that users can only see the pages and such that they
    should be seeing.
    """
    @classmethod
    def setUpClass(cls):
        reset_db()
        cls.client = app.test_client()
        user_datastore.create_user(email="foo@foo.com", password="password")
        user_datastore.create_user(email="bar@bar.com", password="password")
        db.session.commit()
        with cls.client.session_transaction() as sess:
            sess["user_id"] = User.query.filter(User.id == 1).one().get_id()
            sess["_fresh"] = True

        project = Project(name="Bar's project", user=2)
        project.save()

        cls.file_path = os.path.join(app.config["UPLOAD_DIR"],
            "upload_test.txt")
        unit = Unit(project=project, path=cls.file_path)
        unit.save()

    def test_list_projects(self):
        """Test to make sure that bar's projects aren't listed for foo.
        """
        result = self.client.get("/projects")

        assert "Bar's project" not in result.data

    def test_view_project(self):
        """Test to make sure that foo can't see bar's project.
        """
        result = self.client.get("/projects/1")

        assert "Bar's project" not in result.data

    def test_view_document(self):
        """Test to make sure that foo can't see bar's file.
        """
        result = self.client.get("/projects/1/documents/1")

        assert "/uploads/1" not in result.data

    def test_get_document(self):
        """Test to make sure that foo can't get bar's file.
        """
        result = self.client.get("/uploads/1")

        with open(self.file_path) as test_file:
            assert result.data is not test_file.read()

class LoggedOutTests(unittest.TestCase):
    """Make sure that logged out users can't see much of anything.
    """

    @classmethod
    def setUpClass(cls):
        """Reset the DB and create a dummy project and document.
        """
        reset_db()
        cls.client = app.test_client()

        project = Project(name="Bar's project", user=2)
        project.save()

        cls.file_path = os.path.join(app.config["UPLOAD_DIR"],
            "upload_test.txt")
        unit = Unit(project=project, path=cls.file_path)
        unit.save()

    def test_list_projects(self):
        """Test to make sure that unauthed users can't see project lists.
        """
        result = self.client.get("/projects")

        assert "Bar's project" not in result.data

    def test_list_files(self):
        """Test to make sure that unauthed users can't see a specific project.
        """
        result = self.client.get("/projects/1")

        assert "upload_test.txt" not in result.data

    def test_file_show(self):
        """Test to make sure that unauthed users can't see a specific file.
        """
        result = self.client.get("/projects/1/documents/1")

        assert "View file" not in result.data

    def test_file_get(self):
        """Make sure unauthed users can't get a specific file.
        """
        result = self.client.get("/uploads/1")

        with open(self.file_path) as test_file:
            assert result.data is not test_file.read()

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
