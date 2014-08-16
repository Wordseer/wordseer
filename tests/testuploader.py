"""Unit tests for the components of the wordseer web interface.
"""

from cStringIO import StringIO
import os
import shutil
import tempfile
import unittest

import mock

from app import app as application
from app import db
from app import user_datastore
from app.models.document import Document
from app.models.documentfile import DocumentFile
from app.models.flask_security import User
from app.models.project import Project
from app.models.structurefile import StructureFile
from app.models.log import *
import database

class ViewsTests(unittest.TestCase):
    def setUp(self):
        """Clear the database for the next unit test.
        """
        self.client = application.test_client()
        database.clean()
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

    @mock.patch("app.uploader.views.process_files", autospec=True)
    def test_projects_bad_process(self, mock_process_files):
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

    @mock.patch("app.uploader.views.process_files", autospec=True)
    def test_projects_process(self, mock_process_files):
        """Test processing a processable project.
        """
        project = Project(name="test", user=self.user)
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.json")
        document_file1.save()
        document_file2.save()

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
        document_file1 = DocumentFile(path="/test/doc1.xml", projects=[project])
        document_file2 = DocumentFile(path="/test/doc2.xml", projects=[project])
        document_file1.save()
        document_file2.save()
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

        assert "You must select at least one document file"

    @mock.patch("app.uploader.views.os", autospec=os)
    def test_project_show_delete(self, mock_os):
        """Test file deletion.
        """
        mock_os.path.isdir.return_value = False

        project = Project(name="test", user=self.user)
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.xml")
        document_file1.save()
        document_file2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "-1",
            "process-selection": ["1", "2"]
            })
        assert "no files in this project" in result.data
        mock_os.remove.assert_any_call(document_file1.path)
        mock_os.remove.assert_any_call(document_file2.path)
        assert mock_os.remove.call_count == 2

    def test_project_show_bad_delete(self):
        """Test a bad file delete request.
        """
        project = Project(name="test", user=self.user)
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.xml")
        document_file1.save()
        document_file2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "-1",
            })

        assert "must select" in result.data
        assert "/projects/1/documents/1" in result.data
        assert "/projects/1/documents/2" in result.data

    @mock.patch("app.uploader.views.process_files", autospec=True)
    def test_project_show_process(self, mock_process_files):
        """Test processing a processable group of files.
        """
        project = Project(name="test", user=self.user)
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.json")
        document_file1.save()
        document_file2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1", "2"]
            })

        assert "Errors have occurred" not in result.data

    @mock.patch("app.uploader.views.process_files", autospec=True)
    def test_project_show_bad_process(self, mock_process_files):
        """Test processing an unprocessable group of files.
        """
        project = Project(name="test", user=self.user, path="/foo")
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.xml")
        document_file1.save()
        document_file2.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": ["1", "2"]
            })

        assert "must include exactly one" in result.data

        structure_file = StructureFile(project=project, path="/foo/bar.json")
        structure_file.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-structure_file": [str(structure_file.id)]
            })
        assert "at least one document" in result.data.lower()

    def test_get_file(self):
        """Run tests on the get_file view.
        """
        file_handle, file_path = tempfile.mkstemp()
        file_handle = os.fdopen(file_handle, "r+")
        file_handle.write("foobar")

        project = Project(user=self.user)

        document_file = DocumentFile(path=file_path, projects=[project])
        document_file.save()

        result = self.client.get("/uploads/1")
        with open(file_path) as test_file:
            assert result.data == file_handle.read()

    def test_document_show(self):
        """Test the detail document view.
        """
        projxyz = Project(name="test project", path="/test-path/",
            user=self.user)
        docxyz = DocumentFile(path="/test-path/test-file.xml",
            projects=[projxyz])

        docxyz.save()
        projxyz.save()

        #TODO: why is this necessary? why does sqlalchemy complain otherwise
        docid = docxyz.id

        result = self.client.get("/projects/1/documents/1")
        assert "/uploads/" + str(docid) in result.data
        assert "test-file.xml" in result.data

    def test_logs(self):
        """Test to make sure that logs are being displayed.
        """

        project1 = Project(name="foo", path="/test-path",
            user=self.user)
        project2 = Project(name="foob", path="/foobar",
            user=self.user)

        logs = [WarningLog(log_item="a", item_value="a", project=project1),
            InfoLog(log_item="b", item_value="b", project=project1),
            ErrorLog(log_item="c", item_value="c", project=project1)]

        project1.document_files = [DocumentFile(path="foo")]
        project2.document_files = [DocumentFile(path="foo")]
        project1.save()
        project2.save()

        result = self.client.get("/projects/1")

        assert "alert alert-warning" in result.data
        assert "alert alert-info" in result.data
        assert "alert alert-danger" in result.data
        assert "<em>a</em>: a" in result.data
        assert "<em>b</em>: b" in result.data
        assert "<em>c</em>: c" in result.data

class AuthTests(unittest.TestCase):
    """Make sure that users can only see the pages and such that they
    should be seeing.
    """
    #TODO: can we make this a classmethod without SQLAlchemy complaining?
    def setUp(self):
        database.clean()
        self.client = application.test_client()
        self.user1 = user_datastore.create_user(email="foo@foo.com",
            password="password")
        self.user2 = user_datastore.create_user(email="bar@bar.com",
            password="password")
        db.session.commit()
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user1.get_id()
            sess["_fresh"] = True

        self.project = Project(name="Bars project", user=self.user2)
        self.project.save()

        file_handle, file_path = tempfile.mkstemp()
        file_handle = os.fdopen(file_handle, "r+")
        file_handle.write("foobar")

        self.file_path = os.path.join(file_path)
        self.document_file = DocumentFile(projects=[self.project],
                path=self.file_path)
        self.document_file.save()

    def test_list_projects(self):
        """Test to make sure that bar's projects aren't listed for foo.
        """
        result = self.client.get("/projects/")

        assert "Bars project" not in result.data

    def test_view_project(self):
        """Test to make sure that foo can't see bar's project.
        """
        result = self.client.get("/projects/" + str(self.project.id))
        assert "Bars project" not in result.data

    def test_view_document(self):
        """Test to make sure that foo can't see bar's file.
        """
        result = self.client.get("/projects/" + str(self.project.id) +
            "/documents/" + str(self.document_file.id))

        assert "/uploads/" + str(self.document_file.id) not in result.data

    def test_get_document(self):
        """Test to make sure that foo can't get bar's file.
        """
        result = self.client.get("/uploads/" + str(self.document_file.id))

        with open(self.file_path) as test_file:
            assert result.data is not test_file.read()

class LoggedOutTests(unittest.TestCase):
    """Make sure that logged out users can't see much of anything.
    """

    #TODO: can we make this a classmethod without sqlalchemy complaining?
    def setUp(self):
        """Reset the DB and create a dummy project and document.
        """
        database.clean()
        self.client = application.test_client()
        user = User()
        db.session.add(user)
        db.session.commit()
        project = Project(name="Bars project", user=user)
        project.save()

        self.file_handle, self.file_path = tempfile.mkstemp()
        self.file = os.fdopen(self.file_handle, "r+")
        self.file.write("foobar")
        self.file_name = os.path.split(self.file_path)[1]

        document_file = DocumentFile(projects=[project], path=self.file_path)
        document_file.save()

    def test_list_projects(self):
        """Test to make sure that unauthed users can't see project lists.
        """
        result = self.client.get("/projects")

        assert "Bars project" not in result.data

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

