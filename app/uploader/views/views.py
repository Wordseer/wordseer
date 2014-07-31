"""
These are all the view functions for the app.
"""

import os
import threading
import shutil
import random
from string import ascii_letters, digits

from flask import config
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask_security.core import current_user
from flask_security.decorators import login_required
from flask.views import View
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import secure_filename

from .. import exceptions
from .. import forms
from .. import helpers
from .. import uploader
from ...models import Document
from ...models import Project
from ...models import Unit
from ...models import User
from app import app
from app import db
from app.models import User
from lib.wordseerbackend.wordseerbackend.collectionprocessor import cp_run

def generate_form_token():
    """Sets a token to prevent double posts."""
    if '_form_token' not in session:
        form_token = ''.join(
            [random.choice(ascii_letters+digits) for i in range(32)])
        session['_form_token'] = form_token
    return session['_form_token']

@uploader.before_request
def check_form_token():
    """Checks for a valid form token in POST requests."""
    if request.method == 'POST':
        token = session.pop('_form_token', None)
        if not token or token != request.form.get('_form_token'):
            redirect(request.url)

class CLPDView(View):
    """This is a pluggable view to handle CLPD (Create, List, Process, Delete)
    views.

    In this application, we have two CLPD views which are in many ways very
    similar: the project listing and the document listing. With this view,
    we can reduce the redundancy.
    """

    #TODO: facilitate delete

    decorators = [login_required]
    methods = ["GET", "POST"]

    def __init__(self, template, create_form, process_form,
        confirm_delete_form):
        """Initializes a CLPD view. kwargs are data passed to the view in
        general.

        :arg str template: The name of the template to use for rendering.
        :arg Form create_form: The form to use for creation.
        :arg Form process_form: The form to use for listing, processing,
        and deleting.
        :arg Form confirm_delete_form: The form to use for confirming a
        deletion.
        """
        self.template = template
        self.create_form = create_form(prefix="create")
        self.process_form = process_form(prefix="process")
        self.confirm_delete_form = confirm_delete_form(prefix="confirm_delete")
        self.template_kwargs = {}

    def delete_object(self, obj, data):
        """Given a Unit or Project object, delete their files,
        database records, and entries in the process form's choices.
        :arg obj: A Unit or Project objects.
        :arg data: The second part of the tuple in the process form, the first
        item being the object's id.
        """

        if os.path.isdir(obj.path):
            shutil.rmtree(obj.path)
            for document in obj.documents:
                db.session.delete(document)
            db.session.commit()
        else:
            os.remove(obj.path)
        self.process_form.selection.delete_choice(obj.id, data)
        db.session.delete(obj)
        db.session.commit()

    def set_choices(self, **kwargs):
        """Set the appropriate choices for the list view.
        """
        raise NotImplementedError()

    def handle_create(self, **kwargs):
        """Perform actions necessary for the create_form.
        """
        raise NotImplementedError()

    def handle_process(self, **kwargs):
        """Perform actions necessary for the process_form.
        """
        raise NotImplementedError()

    def reset_fields(self):
        """If necessary, reset fields.
        """
        self.create_form.submitted.data = "true"
        self.process_form.submitted.data = "true"

    def pre_tests(self, **kwargs):
        """If necessary, run checks before continuing with the view logic.
        """
        pass

    def dispatch_request(self, **kwargs):
        """Render the template with the required data. kwargs are data
        passed to the URL.
        """
        self.pre_tests(**kwargs)

        self.set_choices(**kwargs)

        if helpers.really_submitted(self.create_form):
            self.handle_create(**kwargs)

        elif helpers.really_submitted(self.process_form):
            self.handle_process(**kwargs)

        self.reset_fields()

        return render_template(self.template,
            create_form=self.create_form,
            process_form=self.process_form,
            **self.template_kwargs)

@uploader.route("/")
def home():
    """Display the home page.
    """
    return render_template("home.html")

class ProjectsCLPD(CLPDView):
    """A CLPD view for the list of a user's projects.
    """
    def __init__(self):
        super(ProjectsCLPD, self).__init__("project_list.html",
            forms.ProjectCreateForm, forms.ProjectProcessForm,
            forms.ConfirmDeleteForm)

    def set_choices(self, **kwargs):
        """Every choice is in the form of (project.id, project.name).
        """
        self.process_form.selection.choices = []
        for project in Project.query.filter(User.id ==
            current_user.id).all():
            self.process_form.selection.add_choice(project.id, project.name)

    def handle_create(self, **kwargs):
        """Created projects are created in the database with a name, a user,
        and a path. Their path is also created.
        """
        project = Project(
            name=self.create_form.name.data,
            user=current_user)
        project.save()
        project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
        project.save()
        os.mkdir(project.path)
        self.process_form.selection.add_choice(project.id, project.name)

    def handle_process(self, **kwargs):
        """For deletion, delete call delete_object on the object and delete
        its path. For processing, send the project to the processor.
        """
        selected_projects = request.form.getlist("process-selection")
        project_objects = [Project.query.get(id) for id in selected_projects]
        if request.form["action"] == self.process_form.DELETE:
            for project in project_objects:
                self.delete_object(project, project.name)
        if request.form["action"] == self.process_form.PROCESS:
            for project in project_objects:
                files = [document for document in project.documents]
                structure_file = helpers.get_structure_file(files)
                process_files(project.path, structure_file.path, project)

uploader.add_url_rule(app.config["PROJECT_ROUTE"],
    view_func=ProjectsCLPD.as_view("projects"))

#TODO: rename this?
class ProjectCLPD(CLPDView):
    """CLPD view for listing files in a project.
    """
    def __init__(self):
        super(ProjectCLPD, self).__init__("document_list.html",
            forms.DocumentUploadForm, forms.DocumentProcessForm,
            forms.ConfirmDeleteForm)
        self.template_kwargs["allowed_extensions"] = \
            [ "." + ext for ext in app.config["ALLOWED_EXTENSIONS"]]

    def pre_tests(self, **kwargs):
        """Make sure this project exists and make sure that this user can see
        the project.
        """
        self.project = helpers.get_object_or_exception(Project,
            Project.id == kwargs["project_id"],
            exceptions.ProjectNotFoundException)

        self.template_kwargs["project"] = self.project

        if self.project.user != current_user.id:
            return app.login_manager.unauthorized()

    def set_choices(self, **kwargs):
        """The template needs the choices in the form of (id, filename).
        """
        file_objects = self.project.documents
        self.process_form.selection.choices = []
        for file_object in file_objects:
            self.process_form.selection.add_choice(file_object.id,
                os.path.split(file_object.path)[1])

    def handle_create(self, **kwargs):
        """For every file, check if it exists and if not then upload it to
        the project directory and create a database record with its filename and
        path.
        """
        uploaded_files = request.files.getlist("create-uploaded_file")
        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                str(self.project.id), filename)
            # TODO: this checks if the file exists, but can we do this
            # inside the form?
            if not os.path.isfile(dest_path):
                uploaded_file.save(dest_path)
                document = Document(path=dest_path, projects=[self.project])
                document.save()
                self.process_form.selection.add_choice(document.id,
                    os.path.split(dest_path)[1])
            else:
                self.create_form.uploaded_file.errors.\
                    append("A file with name " + os.path.split(dest_path)[1] +
                    " already exists")

    def handle_process(self, **kwargs):
        """If deleting, delete every database record and file. If processing,
        then send files to the processor.
        """
        files = request.form.getlist("process-selection")
        file_objects = [Document.query.get(id) for id in files]
        if request.form["action"] == self.process_form.DELETE:
            # Delete every selected file, its database record, and item in
            # the listing
            for file_object in file_objects:
                file_name = os.path.split(file_object.path)[1]
                self.delete_object(file_object, file_name)
        elif request.form["action"] == self.process_form.PROCESS:
            structure_file = helpers.get_structure_file(file_objects)
            process_files(self.project.path, structure_file.path, self.project)

uploader.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>",
    view_func=ProjectCLPD.as_view("project_show"))

@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>" +
    app.config["DOCUMENT_ROUTE"] + '<int:document_id>')
@login_required
def document_show(project_id, document_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """
    #TODO: good spot for a helper
    #document = helpers.get_object_or_exception(Unit,
    #   Unit.id == document_id, exceptions.DocumentNotFoundException)
    try:
        document = Document.query.get(document_id)
    except TypeError:
        return app.login_manager.unauthorized()

    access_granted = current_user.has_document(Document.query.get(document_id))

    # Test if this user can see it
    if not access_granted:
        return app.login_manager.unauthorized()

    filename = os.path.split(document.path)[1]
    #TODO: move to objects
    project = Project.query.join(User).filter(User.id == current_user.id).\
        filter(Document.id == document_id).one()

    return render_template("document_show.html",
        document=document,
        project=project,
        filename=filename)

@uploader.route(app.config["UPLOAD_ROUTE"] + "<int:file_id>")
@login_required
def get_file(file_id):
    """If the user has permission to view this file, then return it.
    """

    document = Document.query.get(file_id)
    try:
        access_granted = current_user.has_document(document)
    except TypeError:
        return app.login_manager.unauthorized()

    # Test if this user can see it
    if not access_granted:
        return app.login_manager.unauthorized()
    directory, filename = os.path.split(document.path)

    return send_from_directory(directory, filename)

def process_files(collection_dir, structure_file, project):
    """Process a list of files using the preprocessor. This must be a valid list
    of files or bad things will happen - exactly one structure file, several
    document files.
    """
    args = (collection_dir, structure_file, app.config["DOCUMENT_EXTENSION"],
        project)
    preprocessing_process = threading.Thread(target=cp_run, args=args)
    preprocessing_process.start()

