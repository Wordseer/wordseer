"""
These are all the view functions for the app.
"""

import os
import shutil
import random
from string import ascii_letters, digits

from flask import (redirect, render_template, request, send_from_directory,
    session)
from flask_security.core import current_user
from flask_security.decorators import login_required
from flask.views import View
from werkzeug import secure_filename

from app import app
from app import db
from . import exceptions
from . import forms
from .models import Unit, Project, User
from . import shortcuts

def generate_form_token():
    """Sets a token to prevent double posts."""
    if '_form_token' not in session:
        form_token = ''.join(
            [random.choice(ascii_letters+digits) for i in range(32)])
        session['_form_token'] = form_token
    return session['_form_token']

@app.before_request
def check_form_token():
    """Checks for a valid form token in POST requests."""
    if request.method == 'POST':
        token = session.pop('_form_token', None)
        if not token or token != request.form.get('_form_token'):
            redirect(request.url)

@app.errorhandler(exceptions.ProjectNotFoundException)
def project_not_found(error):
    """This handles the user trying to view a project that does not exist.
    """
    return shortcuts.not_found("project")

@app.errorhandler(exceptions.DocumentNotFoundException)
def document_not_found(error):
    """This handles the user trying to view a document that does not exist.
    """
    return shortcuts.not_found("document")

@app.errorhandler(404)
def page_not_found(error):
    """This handles the user trying to view a general page that does not exist.
    """
    return shortcuts.not_found("page")

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

    def __init__(self, template, create_form, process_form, **kwargs):
        """Initializes a CLPD view. kwargs are data passed to the view in
        general.

        :arg str template: The name of the template to use for rendering.
        :arg Form create_form: The form to use for creation.
        :arg Form process_form: The form to use for listing, processing,
        and deleting.
        """
        self.template = template
        self.create_form = create_form(prefix="create")
        self.process_form = process_form(prefix="process")
        self.template_kwargs = {}

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

        if shortcuts.really_submitted(self.create_form):
            self.handle_create(**kwargs)

        elif shortcuts.really_submitted(self.process_form):
            self.handle_process(**kwargs)

        self.reset_fields()

        return render_template(self.template,
            create_form=self.create_form,
            process_form=self.process_form,
            **self.template_kwargs)

@app.route("/")
def home():
    """Display the home page.
    """
    return render_template("home.html")

class ProjectsCLPD(CLPDView):
    def __init__(self):
        super(ProjectsCLPD, self).__init__("project_list.html",
            forms.ProjectCreateForm, forms.ProjectProcessForm)

    def set_choices(self, **kwargs):
        self.process_form.selection.choices = []
        for project in Project.query.filter(Project.user ==
            current_user.id).all():
            self.process_form.selection.add_choice(project.id, project.name)

    def handle_create(self, **kwargs):
        #TODO: can we only save this once?
        project = Project(
            name=self.create_form.name.data,
            user=current_user.id)
        project.save()
        project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
        project.save()
        os.mkdir(project.path)
        self.process_form.selection.add_choice(project.id, project.name)

    def handle_process(self, **kwargs):
        selected_projects = request.form.getlist("process-selection")
        if request.form["action"] == self.process_form.DELETE:
            for project_id in selected_projects:
                project = Project.query.filter(Project.id == project_id).one()
                shutil.rmtree(project.path)
                self.process_form.selection.delete_choice(project.id,
                    project.name)
                db.session.delete(project)
                db.session.commit()
        if request.form["action"] == self.process_form.PROCESS:
            #TODO: process the projects
            pass

app.add_url_rule(app.config["PROJECT_ROUTE"],
    view_func=ProjectsCLPD.as_view("projects"))

#TODO: rename this?
class ProjectCLPD(CLPDView):
    def __init__(self):
        super(ProjectCLPD, self).__init__("document_list.html",
            forms.DocumentUploadForm, forms.DocumentProcessForm)
        self.template_kwargs["allowed_extensions"] = \
            app.config["ALLOWED_EXTENSIONS"]

    def pre_tests(self, **kwargs):
        self.project = shortcuts.get_object_or_exception(Project, Project.id,
            kwargs["project_id"], exceptions.ProjectNotFoundException)

        self.template_kwargs["project"] = self.project

        # Test if this user can see it
        if self.project.user is not current_user.id:
            return app.login_manager.unauthorized()

    def set_choices(self, **kwargs):
        # The template needs access to the ID of each file and its filename.
        file_objects = Unit.query.filter(Unit.project_id == self.project.id).\
            filter(Unit.path != None).all()
        self.process_form.selection.choices = []
        for file_object in file_objects:
            self.process_form.selection.add_choice(file_object.id,
                os.path.split(file_object.path)[1])

    def handle_create(self, **kwargs):
        uploaded_files = request.files.getlist("create-uploaded_file")
        print uploaded_files
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
                    append("A file with this name already exists")

    def handle_process(self, **kwargs):
        files = request.form.getlist("process-selection")
        if request.form["action"] == self.process_form.DELETE:
            # Delete every selected file, its database record, and item in
            # the listing
            for file_id in files:
                file_model = Unit.query.filter(Unit.id == file_id).one()
                file_name = os.path.split(file_model.path)[1]
                os.remove(file_model.path)
                db.session.delete(file_model)
                db.session.commit()
                self.process_form.selection.delete_choice(int(file_id),
                    file_name)

app.add_url_rule(app.config["PROJECT_ROUTE"] + "<project_id>",
    view_func=ProjectCLPD.as_view("project_show"))        

@app.route(app.config["PROJECT_ROUTE"] + "<project_id>" +
    app.config["DOCUMENT_ROUTE"] + '<document_id>')
@login_required
def document_show(project_id, document_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """

    project = shortcuts.get_object_or_exception(Project, Project.id,
        project_id, exceptions.ProjectNotFoundException)

    # Test if this user can see it
    if project.user is not current_user.id:
        return app.login_manager.unauthorized()

    document = shortcuts.get_object_or_exception(Unit, Unit.id, document_id,
        exceptions.DocumentNotFoundException)

    filename = os.path.split(document.path)[1]

    return render_template("document_show.html",
        document=document,
        project=project,
        filename=filename)

@app.route(app.config["UPLOAD_ROUTE"] + "<file_id>")
@login_required
def get_file(file_id):
    """If the user has permission to view this file, then return it.
    """

    unit = Unit.query.filter(Unit.id == file_id).one()

    # Test if this user can see it
    if unit.project.user is not current_user.id or not unit.path:
        return app.login_manager.unauthorized()

    directory, filename = os.path.split(unit.path)

    return send_from_directory(directory, filename)
