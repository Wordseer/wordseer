"""
Unit tests for the components of the wordseer web interface.
"""

from cStringIO import StringIO
import os
import shutil
import tempfile
import unittest
import pdb

from flask_security.utils import login_user
import mock
from sqlalchemy import create_engine

from app import app as application
from app import db
from app import user_datastore
from app.models.document import Document
from app.models.dependency import Dependency
from app.models.flask_security import User
from app.models.property import Property
from app.models.project import Project
from app.models.sentence import Sentence
from app.models.sequence import Sequence
from app.models.unit import Unit
from app.models.word import Word
import database

class TestModels(unittest.TestCase):
    def setUp(self):
        database.restore_cache()

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

        sen1 = Sentence()
        sen2 = Sentence()

        word_2.sentences = [sen1, sen2]

        db.session.add_all([sen1, sen2])
        db.session.commit()

        assert word_2.sentences == [sen1, sen2]

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

        #Test with Dependencies
        dependency1 = Dependency()
        dependency2 = Dependency()

        sentence.dependencies = [dependency1, dependency2]

        db.session.add_all([dependency1, dependency2])
        db.session.commit()

        #Test with Sequences
        sequence1 = Sequence()
        sequence2 = Sequence()

        sentence.sequences = [sequence1, sequence2]

        db.session.add_all([sequence1, sequence2])
        db.session.commit()

    def test_model_dependency(self):
        """Test to make sure that Dependency is working properly.
        """

        dependency = Dependency()
        dependency.save()

        # Test with sentences
        sentence1 = Sentence()
        sentence2 = Sentence()
        dependency.sentences = [sentence1, sentence2]

        db.session.add_all([sentence1, sentence2])
        db.session.commit()

    def test_model_sequence(self):
        """Test to make sure that Sequence is working properly.
        """

        sequence = Sequence()
        sequence.save()

        # Test with Sentences
        sentence1 = Sentence()
        sentence2 = Sentence()
        sequence.sentences = [sentence1, sentence2]

        db.session.add_all([sentence1, sentence2])

    def test_model_unit(self):
        """Test to make sure that Unit is working properly.
        """

        unit_type = Property(name="unit_type", value="section")
        number = 1

        unit = Unit()

        unit.properties = [unit_type]
        unit.number = number

        assert unit.number == number

        sentence = Sentence()
        sentence.words = [Word(word="hello"), Word(word="world")]
        prop = Property(name="title", value="Hello World")

        unit.sentences.append(sentence)
        unit.properties.append(prop)

        assert unit.sentences == [sentence]
        assert unit.properties == [unit_type, prop]

        unit.save()
        prop.save()

        retrieved_prop = Property.query.filter(Property.name=="title").\
            filter(Property.value == "Hello World").first()

        assert retrieved_prop.unit.type == "unit"
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

    def test_model_document(self):
        """Test to make sure that Document is working properly.
        """

        d1 = Document(title="test", path="/path/to/d1")
        d1.save()

        assert d1.type == "document"

        u1 = Unit()
        u1.save()

        d1.children.append(u1)
        d1.save()

        assert d1.children == [u1]
        assert u1.parent == d1

class ViewsTests(unittest.TestCase):
    def setUp(self):
        """Clear the database for the next unit test.
        """
        self.client = application.test_client()
        database.restore_cache()
        self.user = user_datastore.create_user(email="foo@foo.com",
            password="password")
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user.id
            sess["_fresh"] = True

    def test_no_projects(self):
        """Test the projects view with no projects present.
        """
        result = self.client.get("/projects/")
        assert "no projects" in result.data

    def test_projects(self):
        """Test the projects view with a project present.
        """
        new_project = Project(name="test", user=self.user)
        new_project.save()
        result = self.client.get("/projects/")
        assert "/projects/1" in result.data

    def test_projects_bad_create(self):
        """Test creating an existing project.
        """
        project = Project(name="test", user=self.user)
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

    @mock.patch("app.uploader.views.os", autospec=os)
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

    @mock.patch("app.uploader.views.shutil", autospec=shutil)
    @mock.patch("app.uploader.views.os", autospec=os)
    def test_projects_delete_post(self, mock_os, mock_shutil):
        """Test project deletion.
        """
        mock_os.path.isdir.return_value = True

        project1 = Project(name="test1", path=application.config["UPLOAD_DIR"],
            user=self.user)
        project2 = Project(name="test2", path=application.config["UPLOAD_DIR"],
            user=self.user)
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

        project1 = Project(name="test1", user=self.user)
        project2 = Project(name="test2", user=self.user)
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

        project1 = Project(name="test1", user=self.user)
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
        project = Project(name="test", user=self.user)
        project.save()

        document1 = Document(projects=[project], path="/test-path/1.xml")
        document2 = Document(projects=[project], path="/test-path/2.json")
        document1.save()
        document2.save()

        result = self.client.post("/projects/", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1"]
            })

        assert "Errors have occurred" not in result.data

    def test_no_project_show(self):
        """Make sure project_show says that there are no files.
        """
        project = Project(name="test", user=self.user)
        project.save()
        result = self.client.get("/projects/1")

        assert "test" in result.data
        assert "There are no files in this project" in result.data

    def test_project_show(self):
        """Make sure project_show shows files.
        """
        project = Project(name="test", user=self.user)
        project.save()
        document1 = Document(path="/test/doc1.xml", projects=[project])
        document2 = Document(path="/test/doc2.xml", projects=[project])
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
        project = Project(name="test", user=self.user)
        project.save()

        upload_dir = tempfile.mkdtemp()
        application.config["UPLOAD_DIR"] = upload_dir
        os.makedirs(os.path.join(upload_dir, "1"))

        result = self.client.post("/projects/1", data={
            "create-submitted": "true",
            "create-uploaded_file": (StringIO("Test file"), "test.xml")
            })

        assert os.path.exists(os.path.join(upload_dir, "1", "test.xml"))
        assert "/projects/1/documents/1" in result.data
        assert "test.xml" in result.data

        uploaded_file = open(os.path.join(upload_dir, "1", "test.xml"))

        assert uploaded_file.read() == "Test file"

    def test_project_show_double_upload(self):
        """Try uploading two files with the same name to the project_show view.
        """
        project = Project(name="test", user=self.user)
        project.save()

        upload_dir = tempfile.mkdtemp()
        application.config["UPLOAD_DIR"] = upload_dir
        os.makedirs(os.path.join(upload_dir, "1"))

        self.client.post("/projects/1", data={
            "create-submitted": "true",
            "create-uploaded_file": (StringIO("Test file"), "test.xml")
            })

        result = self.client.post("/projects/1", data={
            "create-submitted": "true",
            "create-uploaded_file": (StringIO("Test file 2"), "test.xml")
            })

        assert "already exists" in result.data

    def test_project_show_no_post(self):
        """Try sending an empty post to project_show.
        """
        project = Project(name="test", user=self.user)
        project.save()

        result = self.client.post("/projects/1", data={
            "create-submitted": "true"
            })

        assert "You must select a file" in result.data

        result = self.client.post("/projects/1", data={
            "process-submitted": "true"
            })

        assert "At least one document must be selected"

    @mock.patch("app.uploader.views.os", autospec=os)
    def test_project_show_delete(self, mock_os):
        """Test file deletion.
        """
        mock_os.path.isdir.return_value = False

        project = Project(name="test", user=self.user)
        project.save()

        document1 = Document(projects=[project], path="/test-path/1.xml")
        document2 = Document(projects=[project], path="/test-path/2.xml")
        document1.save()
        document2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "-1",
            "process-selection": ["1", "2"]
            })

        assert "no files in this project" in result.data
        mock_os.remove.assert_any_call(document1.path)
        mock_os.remove.assert_any_call(document2.path)
        assert mock_os.remove.call_count == 2

    def test_project_show_bad_delete(self):
        """Test a bad file delete request.
        """
        project = Project(name="test", user=self.user)
        project.save()

        unit1 = Document(projects=[project], path="/test-path/1.xml")
        unit2 = Document(projects=[project], path="/test-path/2.xml")
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
        project = Project(name="test", user=self.user)
        project.save()

        unit1 = Document(projects=[project], path="/test-path/1.xml")
        unit2 = Document(projects=[project], path="/test-path/2.json")
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
        project = Project(name="test", user=self.user)
        project.save()

        unit1 = Document(projects=[project], path="/test-path/1.xml")
        unit2 = Document(projects=[project], path="/test-path/2.xml")
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


    @unittest.skip("Query not working")
    def test_get_file(self):
        """Run tests on the get_file view.
        """
        file_handle, file_path = tempfile.mkstemp()
        file_handle = os.fdopen(file_handle, "r+")
        file_handle.write("foobar")

        project = Project(user=self.user)

        document = Document(path=file_path, projects=[project])
        document.save()

        result = self.client.get("/uploads/1")
        with open(file_path) as test_file:
            assert result.data == file_handle.read()

    def test_document_show(self):
        """Test the detail document view.
        """
        projxyz = Project(name="test project", path="/test-path/",
            user=self.user)
        docxyz = Document(path="/test-path/test-file.xml", projects=[projxyz])

        docxyz.save()
        projxyz.save()

        #TODO: why is this necessary? why does sqlalchemy complain otherwise
        docid = docxyz.id

        result = self.client.get("/projects/1/documents/1")
        assert "/uploads/" + str(docid) in result.data
        assert "test-file.xml" in result.data



class AuthTests(unittest.TestCase):
    """Make sure that users can only see the pages and such that they
    should be seeing.
    """
    #TODO: can we make this a classmethod without SQLAlchemy complaining?
    def setUp(self):
        database.restore_cache()
        self.client = application.test_client()
        self.user1 = user_datastore.create_user(email="foo@foo.com",
            password="password")
        self.user2 = user_datastore.create_user(email="bar@bar.com",
            password="password")
        db.session.commit()
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user1.get_id()
            sess["_fresh"] = True

        self.project = Project(name="Bar's project", user=self.user2)
        self.project.save()

        file_handle, file_path = tempfile.mkstemp()
        file_handle = os.fdopen(file_handle, "r+")
        file_handle.write("foobar")

        self.file_path = os.path.join(file_path)
        self.document = Document(projects=[self.project], path=self.file_path)
        self.document.save()

    def test_list_projects(self):
        """Test to make sure that bar's projects aren't listed for foo.
        """
        result = self.client.get("/projects/")

        assert "Bar's project" not in result.data

    def test_view_project(self):
        """Test to make sure that foo can't see bar's project.
        """
        result = self.client.get("/projects/" + str(self.project.id))

        assert "Bar's project" not in result.data

    def test_view_document(self):
        """Test to make sure that foo can't see bar's file.
        """
        result = self.client.get("/projects/" + str(self.project.id) +
            "/documents/" + str(self.document.id))

        assert "/uploads/" + str(self.document.id) not in result.data

    def test_get_document(self):
        """Test to make sure that foo can't get bar's file.
        """
        result = self.client.get("/uploads/" + str(self.document.id))

        with open(self.file_path) as test_file:
            assert result.data is not test_file.read()

class LoggedOutTests(unittest.TestCase):
    """Make sure that logged out users can't see much of anything.
    """

    #TODO: can we make this a classmethod without sqlalchemy complaining?
    def setUp(self):
        """Reset the DB and create a dummy project and document.
        """
        database.restore_cache()
        self.client = application.test_client()
        user = User()
        db.session.add(user)
        db.session.commit()
        project = Project(name="Bar's project", user=user)
        project.save()

        self.file_handle, self.file_path = tempfile.mkstemp()
        self.file = os.fdopen(self.file_handle, "r+")
        self.file.write("foobar")
        self.file_name = os.path.split(self.file_path)[1]

        document = Document(projects=[project], path=self.file_path)
        document.save()

    def test_list_projects(self):
        """Test to make sure that unauthed users can't see project lists.
        """
        result = self.client.get("/projects")

        assert "Bar's project" not in result.data

    def test_list_files(self):
        """Test to make sure that unauthed users can't see a specific project.
        """
        result = self.client.get("/projects/1")

        assert self.file_name not in result.data

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

