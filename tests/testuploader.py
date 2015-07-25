"""Unit tests for the components of the wordseer web interface.
"""
import pdb
from cStringIO import StringIO
import os
import shutil
import tempfile
import unittest

from json import loads

import mock

from app import app as application
from app import db
from app import user_datastore
from app.models.document import Document
from app.models.documentfile import DocumentFile
from app.models.flask_security import User
from app.models.project import Project
from app.models.association_objects import ProjectsUsers
from app.models.structurefile import StructureFile
from app.models.log import *
import database

class ViewsTests(unittest.TestCase):
    def setUp(self):
        """Clear the database for the next unit test.
        """
        self.client = application.test_client()
        database.clean()
        self.user = user_datastore.create_user(email="foo@bar.com",
            password="password")
        db.session.add(self.user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            db.session.add(self.user)
            sess["user_id"] = self.user.id
            sess["_fresh"] = True

    def tearDown(self):
        db.session.remove()

    def test_no_projects(self):
        """Test the projects view with no projects present.
        """
        result = self.client.get(application.config["PROJECT_ROUTE"])
        assert "You own no projects." in result.data

    def test_projects(self):
        """Test the projects view with a project present.
        """
        new_project = Project(name="test", users=[self.user])
        new_project.save()
        result = self.client.get("/projects/")
        assert "/projects/1" in result.data

    @unittest.skip("the uploader currently lets you create projects duplicate names")
    def test_projects_bad_create(self):
        """Test creating an existing project.
        """
        project = Project(name="test", users=[self.user])
        project.save()

        result = self.client.post("/projects/", data={
            "create-submitted": "true",
            "create-name": "test"
            })

        assert "already exists" in result.data

    @unittest.skip("the uploader currently lets you create projects duplicate names")
    def test_projects_duplicate_create(self):
        """Test creating a project with the same name as another user's.
        """
        project = Project(name="test", users=[User()])
        project.save()

        result = self.client.post("/projects/", data={
            "create-submitted": "true",
            "name": "test"
            })

        assert "already exists" not in result.data

    @unittest.skip("the uploader lets you create a project without a name (maybe it shouldn't?)")
    def test_projects_empty_post(self):
        """Test POSTing without a project name to the projects view.
        """
        result = self.client.post(application.config["PROJECT_ROUTE"] + "new", data={
            "name": ""
            })

        print result.data
        assert "no projects" in result.data
        assert "You must provide a name" in result.data

    @mock.patch("app.uploader.views.views.os", autospec=os)
    def test_projects_valid_create_post(self, mock_os):
        """Test POSTing with a valid project name.
# 
        The view should have the name and the path to the project.
        """
        mock_os.path.join.return_value = "test_path"

        result = self.client.post(application.config["PROJECT_ROUTE"] + "new", data={
            "name": "test project"
        })

        print result.data
        assert '"errors": []' in result.data

    @mock.patch("app.uploader.views.views.shutil", autospec=shutil)
    @mock.patch("app.uploader.views.views.os", autospec=os)
    def test_projects_delete_post(self, mock_os, mock_shutil):
        """Test project deletion.
        """
        mock_os.path.isdir.return_value = True

        project1 = Project(name="test1", path=application.config["UPLOAD_DIR"])
        db.session.add(project1)
        self.user.add_project(project1, role=ProjectsUsers.ROLE_ADMIN)
        pid = str(project1.id)

        result = self.client.post(application.config["DELETE_ROUTE"], data={
            "project_id": pid,
            "obj_type": "project",
            "obj_id": pid,
            })

        db.session.add(project1)
        assert '"obj_type": "project",' in result.data
        assert '"obj_id": %s' % pid in result.data
        assert project1.deleted
        # not actually deleting the dir anymore, pending a garbage collection process
        # mock_shutil.rmtree.assert_any_call(project1.path)
        # assert mock_shutil.rmtree.call_count == 1

    def test_projects_delete_no_perms(self):
        """Delete projects without proper permissions.
        """
        project = Project(name="foo")
        rel = self.user.add_project(project, role=ProjectsUsers.ROLE_USER)
        project.save()

        result = self.client.post(application.config["DELETE_ROUTE"], data={
            "project_id": project.id,
            "obj_type": "project",
            "obj_id": project.id,
            })

        print result.data
        assert "login?next=%2Fdelete%2F" in result.data

    def test_no_project_show(self):
        """Make sure project_show says that there are no files.
        """
        project = Project(name="test", users=[self.user])
        project.save()
        result = self.client.get(application.config["PROJECT_ROUTE"] + str(project.id))

        assert "test" in result.data
        assert "There are no Documents in this project." in result.data

    def test_project_show(self):
        """Make sure project_show shows files.
        """
        project = Project(name="test", users=[self.user])
        project.save()
        document_file1 = DocumentFile(path="/test/doc1.xml", projects=[project])
        document_file2 = DocumentFile(path="/test/doc2.xml", projects=[project])
        document_file1.save()
        document_file2.save()
        result = self.client.get("/projects/1")

        assert "doc1.xml" in result.data
        assert "doc2.xml" in result.data
        assert application.config["UPLOAD_ROUTE"] + "doc/%s" % document_file1.id in result.data
        assert application.config["UPLOAD_ROUTE"] + "doc/%s" % document_file2.id in result.data

    def test_project_show_upload(self):
        """Try uploading a file to the project_show view.
        """

        project = Project(name="test")
        db.session.add(project)
        self.user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
        project.save()

        pid = str(project.id)

        upload_dir = tempfile.mkdtemp()
        application.config["UPLOAD_DIR"] = upload_dir
        os.makedirs(os.path.join(upload_dir, pid))

        result = self.client.post(application.config["PROJECT_ROUTE"] + pid + "/upload", data={
            "uploaded_file": (StringIO("<thing>Test file</thing>"), "test.xml")
            })

        data = loads(result.data)
        # validation error contains "The file test.xml is not well-formed XML."
        assert os.path.exists(os.path.join(upload_dir, pid, "test.xml"))
        assert data["files"][0]["type"] == "doc"
        assert data["files"][0]["filename"] == "test.xml"

        uploaded_file = open(os.path.join(upload_dir, pid, "test.xml"))

        assert uploaded_file.read() == "<thing>Test file</thing>"

    def test_project_show_double_upload(self):
        """Try uploading two files with the same name to the project_show view.
        """
        project = Project(name="test")
        db.session.add(project)
        self.user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
        project.save()

        pid = str(project.id)

        upload_dir = tempfile.mkdtemp()
        application.config["UPLOAD_DIR"] = upload_dir
        os.makedirs(os.path.join(upload_dir, pid))

        result = self.client.post(application.config["PROJECT_ROUTE"] + pid + "/upload", data={
            "uploaded_file": (StringIO("<thing>Test file</thing>"), "test.xml")
            })

        result = self.client.post(application.config["PROJECT_ROUTE"] + pid + "/upload", data={
            "uploaded_file": (StringIO("<thing>Test file 2</thing>"), "test.xml")
            })

        assert "already exists" in result.data

    @unittest.skip("view doesn't work this way anymore, write new tests for processing and uploads")
    def test_project_show_no_post(self):
        """Try sending an empty post to project_show.
        """
        project = Project(name="test")
        self.user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
        project.save()

        result = self.client.post("/projects/1", data={
            "create-submitted": "true"
            })

        assert "You must select a file" in result.data

        result = self.client.post("/projects/1", data={
            "process-submitted": "true"
            })

        assert "You must select at least one document file"

    @mock.patch("app.uploader.views.views.os", autospec=os)
    def test_project_show_delete(self, mock_os):
        """Test file deletion.
        """
        mock_os.path.isdir.return_value = False

        project = Project(name="test")
        db.session.add(project)
        self.user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
        project.save()
        pid = str(project.id)

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.xml")
        db.session.add_all([document_file1, document_file2])
        document_file1.save()
        document_file2.save()

        result = self.client.post(application.config["DELETE_ROUTE"], data={
            "project_id": pid,
            "obj_type": "doc",
            "obj_id": document_file1.id
            })

        assert '"obj_type": "doc",' in result.data
        assert '"obj_id": %s' % document_file1.id in result.data 
        mock_os.remove.assert_any_call("/test-path/1.xml")
        # mock_os.remove.assert_any_call("/test-path/2.xml")
        assert mock_os.remove.call_count == 1

    def test_project_show_bad_delete(self):
        """Test a bad file delete request.
        """
        project = Project(name="test", users=[self.user])
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.xml")
        document_file1.save()
        document_file2.save()

        result = self.client.post(application.config["DELETE_ROUTE"], data={
            "project_id": project.id,
            "obj_type": "doc",
            # missing the object id
            })

        assert '"status": "OK"' not in result.data

    @mock.patch("app.uploader.views.views.process_files", autospec=True)
    def test_project_show_process(self, mock_process_files):
        """Test processing a processable group of files.
        """
        #TODO: why is this passing?
        project = Project(name="test", users=[self.user])
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

    def test_project_show_process_no_perms(self):
        """Process files without proper permissions.
        """
        project = Project(name="foo")
        rel = self.user.add_project(project, role=ProjectsUsers.ROLE_USER)
        document_file = DocumentFile(projects=[project], path="/foo/bar.xml")
        structure_file = StructureFile(project=project, path="/foo/bar.json")
        document_file.save()
        structure_file.save()
        project.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "0",
            "process-selection": [str(document_file.id)],
            "process-structure_file": str(structure_file.id)
            })

        assert "You can&#39;t do that" in result.data

    def test_project_show_process_no_perms(self):
        """Delete files without proper permissions.
        """
        project = Project(name="foo")
        rel = self.user.add_project(project, role=ProjectsUsers.ROLE_USER)
        document_file1 = DocumentFile(projects=[project], path="/foo/bar.xml")
        structure_file1 = StructureFile(project=project, path="/foo/bar.json")
        project.save()

        result = self.client.post("/projects/1", data={
            "process-submitted": "true",
            "action": "-1",
            "process-selection": ["1"]
            })

        assert '"status": "OK",' not in result.data

    @mock.patch("app.uploader.views.views.process_files", autospec=True)
    def test_project_show_bad_process(self, mock_process_files):
        """Test processing an unprocessable group of files.
        """
        project = Project(name="test", path="/foo")
        rel = self.user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
        db.session.add(project)
        project.save()

        document_file1 = DocumentFile(projects=[project],
            path="/test-path/1.xml")
        document_file2 = DocumentFile(projects=[project],
            path="/test-path/2.xml")
        db.session.add_all([document_file1, document_file2])
        document_file1.save()
        document_file2.save()

        result = self.client.post(application.config["PROCESS_ROUTE"] + str(project.id), data={
            "struc_id": 555
            })
        assert '"status": "OK",' not in result.data

    def test_get_file(self):
        """Run tests on the get_file view.
        """
        file_handle, file_path = tempfile.mkstemp()
        file_handle = os.fdopen(file_handle, "r+")
        file_handle.write("foobar")

        project = Project(users=[self.user])

        document_file = DocumentFile(path=file_path, projects=[project])
        document_file.save()

        result = self.client.get(application.config["UPLOAD_ROUTE"] + "doc/%s" % document_file.id)
        with open(file_path) as test_file:
            assert result.data == file_handle.read()

    def test_logs(self):
        """Test to make sure that logs are being displayed.
        """

        project1 = Project(name="log test project", path="/log-test-path")
    
        self.user.add_project(project1, role=ProjectsUsers.ROLE_ADMIN)

        logs = [WarningLog(log_item="a", item_value="a", project=project1),
            InfoLog(log_item="b", item_value="b", project=project1),
            ErrorLog(log_item="c", item_value="c", project=project1)]

        project1.document_files = [DocumentFile(path="foo")]
        db.session.add(project1)
        db.session.commit()

        result = self.client.get(application.config["PROJECT_ROUTE"] + str(project1.id))

        print result.data
        assert "log test project" in result.data
        assert "processlog alert alert-warning" in result.data
        assert "processlog alert alert-warning hidden" not in result.data
        assert "processlog alert alert-info" in result.data
        assert "processlog alert alert-info hidden" not in result.data
        assert "processlog alert alert-danger" in result.data
        assert "processlog alert alert-danger hidden" not in result.data
        assert "<em>a</em>: a" in result.data
        assert "<em>b</em>: b" in result.data
        assert "<em>c</em>: c" in result.data

    def test_process_processed_files(self):
        """Make sure that a project that's being processed or already
        processed can't be processed again.
        """

        project1 = Project(name="foo", path="/test-path",
            status=Project.STATUS_PREPROCESSING)
        rel = self.user.add_project(project1, role=ProjectsUsers.ROLE_ADMIN)
        document_file = DocumentFile(path="foo/foo.xml")
        structure_file = StructureFile(path="foo/foo.json")
        project1.document_files = [document_file]
        project1.structure_files = [structure_file]
        project1.save()

        data = {
            "struc_id": structure_file.id,
            }

        result = self.client.post(application.config["PROCESS_ROUTE"] + str(project1.id), data=data)

        assert '"status": "OK"' not in result.data

        project1.status = Project.STATUS_DONE
        project1.save()

        result = self.client.post(application.config["PROCESS_ROUTE"] + str(project1.id), data=data)

        assert '"status": "OK"' not in result.data

class ProjectPermissionsTests(unittest.TestCase):
    """Tests for the ProjectPermissions view.
    """
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
        self.project1 = Project(name="Foos project")
        self.project2 = Project(name="Bars project")
        self.user1.add_project(self.project1, ProjectsUsers.ROLE_ADMIN)
        self.user2.add_project(self.project2, ProjectsUsers.ROLE_ADMIN)
        self.project1.save()
        self.project2.save()

    def test_permissions_access(self):
        """Make sure users can only access their own permissions.
        """
        result = self.client.get("/projects/2/permissions")
        assert result.status_code == 302
        assert "Permissions" not in result.data
        result = self.client.get("/projects/1/permissions")
        assert "Permissions" in result.data

    def test_create_nonexistent(self):
        """Add a nonexistent user.
        """

        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "1",
            "permissions-new_collaborator": "gjie"
            })

        assert result.status_code == 200
        assert "This user does not exist." in result.data

    def test_create_existing(self):
        """Add an existing user.
        """
        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "1",
            "permissions-new_collaborator": "foo@foo.com"
            })

        assert result.status_code == 200
        assert "This user is already on this project" in result.data

    def test_create_proper(self):
        """Do a proper add.
        """

        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "1",
            "permissions-new_collaborator": "bar@bar.com",
            "permissions-create_permissions": "1"
            })

        assert result.status_code == 200
        assert "bar@bar.com</label>" in result.data

    def test_delete_nonexistant(self):
        """Try to delete without a selection.
        """

        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "-1",
            })

        assert result.status_code == 200
        assert "must make a selection" in result.data

    def test_delete(self):
        """Try to delete a selection.
        """
        rel = self.user2.add_project(self.project1, ProjectsUsers.ROLE_ADMIN)
        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "-1",
            "permissions-selection": [str(rel.id)]
            })

        assert result.status_code == 200
        assert "bar@bar.com" not in result.data

    def test_update(self):
        """Try to update a user's permissions.
        """
        rel = self.user2.add_project(self.project1, ProjectsUsers.ROLE_USER)
        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "0",
            "permissions-selection": [str(rel.id)],
            "permissions-update_permissions": ["1"]
            })

        assert result.status_code == 200
        assert "User</td>" not in result.data

    def test_role_access(self):
        """Make sure that regular users can't see permissions of a project
        they have.
        """

        rel = self.user1.add_project(self.project1, ProjectsUsers.ROLE_USER)

        result = self.client.get("/projects/2/permissions")

        assert result.status_code == 302
        assert "Bars project" not in result.data

    def test_final_delete(self):
        """Make sure that there is always at least one user with admin
        privileges on a project.
        """

        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "-1",
            "permissions-selection": ["1"]
            })

        assert result.status_code == 200
        assert "At least one user" in result.data
        assert "foo@foo.com</label>" in result.data

    def test_final_update(self):
        """Make sure that at least one user has admin privileges.
        """

        result = self.client.post("/projects/1/permissions", data={
            "permissions-submitted": "true",
            "action": "0",
            "permissions-selection": ["1"],
            "permissions-update_permissions": ["0"]
            })

        assert result.status_code == 200
        assert "At least one user" in result.data
        assert "User</td>" not in result.data

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

        self.project = Project(name="Bars project")
        self.user2.add_project(self.project, role=ProjectsUsers.ROLE_ADMIN)

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
    @classmethod
    def setUpClass(cls):
        """Reset the DB and create a dummy project and document.
        """
        database.clean()
        cls.client = application.test_client()
        user = User()
        db.session.add(user)
        db.session.commit()
        project = Project(name="Bars project", users=[user])
        project.save()

        cls.file_handle, cls.file_path = tempfile.mkstemp()
        cls.file = os.fdopen(cls.file_handle, "r+")
        cls.file.write("foobar")
        cls.file_name = os.path.split(cls.file_path)[1]

        document_file = DocumentFile(projects=[project], path=cls.file_path)
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

