"""
These are all the view functions for the app.
"""

import os
import shutil
import random
from string import ascii_letters, digits

from flask import (redirect, render_template, request, send_from_directory,
    session, config)
from flask_security.core import current_user
from flask_security.decorators import login_required
from flask.views import View
from werkzeug import secure_filename

from app import app
from app import db
from app.models import User
from .. import exceptions
from .. import forms
from ...models import Unit, Project
from .. import helpers
from .. import uploader

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
            for unit in obj.files:
                db.session.delete(unit)
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
        self.process_form.submitted.dat = "true"

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
        for project in Project.query.filter(Project.user ==
            current_user.id).all():
            self.process_form.selection.add_choice(project.id, project.name)

    def handle_create(self, **kwargs):
        """Created projects are created in the database with a name, a user,
        and a path. Their path is also created.
        """
        project = Project(
            name=self.create_form.name.data,
            user=current_user.id)
        db.session.add(project)
        db.session.flush()
        project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
        project.save()
        os.mkdir(project.path)
        self.process_form.selection.add_choice(project.id, project.name)

    def handle_process(self, **kwargs):
        """For deletion, delete call delete_object on the object and delete
        its path. For processing, send the project to the processor.
        """
        selected_projects = request.form.getlist("process-selection")
        if request.form["action"] == self.process_form.DELETE:
            for project_id in selected_projects:
                project = Project.query.filter(Project.id == project_id).one()
                self.delete_object(project, project.name)
        if request.form["action"] == self.process_form.PROCESS:
            #TODO: process the projects
            pass

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
        file_objects = Unit.query.filter(Unit.project_id == self.project.id).\
            filter(Unit.path != None).all()
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
                unit = Unit(path=dest_path, project=self.project)
                unit.save()
                self.process_form.selection.add_choice(unit.id,
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
        if request.form["action"] == self.process_form.DELETE:
            # Delete every selected file, its database record, and item in
            # the listing
            for file_id in files:
                file_model = Unit.query.filter(Unit.id == file_id).one()
                file_name = os.path.split(file_model.path)[1]
                self.delete_object(file_model, file_name)
        elif request.form["action"] == self.process_form.PROCESS:
            pass

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

    document = helpers.get_object_or_exception(Unit,
        Unit.id == document_id, exceptions.DocumentNotFoundException)

    # Test if this user can see it
    if document.project.user != current_user.id:
        return app.login_manager.unauthorized()

    filename = os.path.split(document.path)[1]

    return render_template("document_show.html",
        document=document,
        project=document.project,
        filename=filename)

@uploader.route(app.config["UPLOAD_ROUTE"] + "<int:file_id>")
@login_required
def get_file(file_id):
    """If the user has permission to view this file, then return it.
    """

    unit = Unit.query.filter(Unit.id == file_id).one()

    # Test if this user can see it
    if unit.project.user != current_user.id or not unit.path:
        return app.login_manager.unauthorized()

    directory, filename = os.path.split(unit.path)

    return send_from_directory(directory, filename)
