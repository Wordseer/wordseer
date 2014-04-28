import os
import shutil
#import random
#from string import ascii_letters, digits

from flask import render_template, request, send_from_directory
from flask.views import View
from werkzeug import secure_filename

from app import app
import exceptions
import forms
from models import Unit, Project
import shortcuts

#TODO: implement after flask-sqlalchemy
#def generate_form_token():
    #"""Sets a token to prevent double posts."""
    #if '_form_token' not in session:
        #form_token = \
            #''.join([random.choice(ascii_letters+digits) for i in range(32)])
        #session['_form_token'] = form_token
    #return session['_form_token']

#@app.before_request
#def check_form_token():
    #"""Checks for a valid form token in POST requests."""
    #if request.method == 'POST':
        #token = session.pop('_form_token', None)
        #if not token or token != request.form.get('_form_token'):
            #redirect(request.url)

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

    def __init__(self,  **kwargs):
        """Initializes a CLPD view. kwargs are data passed to the view in
        general.
        """
        #self.template = template
        self.kwargs = kwargs

    def dispatch_request(self, **kwargs):
        """Render the template with the required data. kwargs are data
        passed to the URL.
        """
        print self.kwargs
        print other
        return "hello world"
        #return render_template(self.template, **kwargs)

app.add_url_rule("/test/<test>", view_func=CLPDView.as_view("test", blah=True))

@app.route("/")
def home():
    return render_template("home.html")

@app.route(app.config["PROJECT_ROUTE"], methods=["GET", "POST"])
def projects():
    """
    This view handles projects. It includes a form at the top to
    create a new project, and under the form the page has a listing of
    already created projects owned by the user.
    """

    create_form = forms.ProjectCreateForm(prefix="create")
    process_form = forms.ProjectProcessForm(prefix="process")

    process_form.selection.choices=[]
    for project in Project.all().all():
        process_form.selection.add_choice(project.id, project.name)

    if shortcuts.really_submitted(create_form):
        #TODO: is this secure? maybe not
        #TODO: can we only save this once?
        project = Project(
            name=create_form.name.data)
        project.save()
        project.path=os.path.join(app.config["UPLOAD_DIR"], str(project.id))
        project.save()
        os.mkdir(project.path)
        process_form.selection.add_choice(project.id, project.name)

    elif shortcuts.really_submitted(process_form):
        selected_projects = request.form.getlist("process-selection")
        if request.form["action"] == process_form.DELETE:
            for project_id in selected_projects:
                project = session.query(Project).\
                    filter(Project.id == project_id).one()
                shutil.rmtree(project.path)
                process_form.selection.delete_choice(project.id, project.name)
                session.delete(project)
                session.commit()
        if request.form["action"] == process_form.DELETE:
            #TODO: process the projects
            pass

    create_form.submitted.data = "true"
    process_form.submitted.data = "true"

    return render_template("project_list.html",
        create_form=create_form,
        process_form=process_form,
        projects=projects)

@app.route(app.config["PROJECT_ROUTE"] + "<project_id>" +
    app.config["DOCUMENT_ROUTE"] + 'create/')
@app.route(app.config["PROJECT_ROUTE"] + "<project_id>",
    methods=["GET", "POST"])
def project_show(project_id):
    """
    Show the files contained in a specific project. It also allows the user
    to upload a new document, much like projects().

    :param int project_id: The ID of the desired project.
    """

    # Test if this project exists
    project = shortcuts.get_object_or_exception(Project, Project.id, project_id,
        exceptions.ProjectNotFoundException)

    upload_form = forms.DocumentUploadForm(prefix="upload")
    process_form = forms.DocumentProcessForm(prefix="process")

    # The template needs access to the ID of each file and its filename.
    file_objects = Unit.filter(Unit.project_id == project_id).\
        filter(Unit.path != None).all()
    process_form.selection.choices=[]
    for file_object in file_objects:
        process_form.selection.add_choice(file_object.id,
            os.path.split(file_object.path)[1])

    # First handle the actions of the upload form
    if shortcuts.really_submitted(upload_form):
        uploaded_files = request.files.getlist("upload-uploaded_file")
        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                str(project_id), filename)
            # TODO: this checks if the file exists, but can we do this
            # inside the form?
            if not os.path.isfile(dest_path):
                uploaded_file.save(dest_path)
                unit = Unit(path=dest_path, project=project)
                unit.save()
                process_form.selection.add_choice(unit.id,
                    os.path.split(dest_path)[1])
            else:
                upload_form.uploaded_file.errors.\
                    append("A file with this name already exists")

    # Or what happened with the document selection
    elif shortcuts.really_submitted(process_form):
        files = request.form.getlist("process-selection")
        if request.form["action"] == process_form.DELETE:
            # Delete every selected file, its database record, and item in
            # the listing
            for file_id in files:
                file_model = session.query(Unit).\
                    filter(Unit.id == file_id).one()
                file_name = os.path.split(file_model.path)[1]
                os.remove(file_model.path)
                session.delete(file_model)
                session.commit()
                process_form.selection.delete_choice(int(file_id), file_name)

        elif request.form["action"] == process_form.PROCESS:
            #TODO: process these files.
            pass

    # TODO: maybe do this a bit better?
    upload_form.submitted.data = "true"
    process_form.submitted.data = "true"

    return render_template("document_list.html",
        project=project,
        upload_form=upload_form,
        process_form=process_form,
        allowed_extensions=app.config["ALLOWED_EXTENSIONS"])

@app.route(app.config["PROJECT_ROUTE"] + "<project_id>" +
    app.config["DOCUMENT_ROUTE"] + '<document_id>')
def document_show(project_id, document_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """

    project = shortcuts.get_object_or_exception(Project, Project.id,
        project_id, exceptions.ProjectNotFoundException)
    document = shortcuts.get_object_or_exception(Unit, Unit.id, document_id,
        exceptions.DocumentNotFoundException)

    filename = os.path.split(document.path)[1]
    
    return render_template("document_show.html",
        document=document,
        project=project,
        filename=filename)

@app.route(app.config["UPLOAD_ROUTE"] + "<file_id>")
def get_file(file_id):
    """If the user has permission to view this file, then return it.
    """

    unit = session.query(Unit).filter(Unit.id == file_id).one()

    directory, filename = os.path.split(unit.path)

    return send_from_directory(directory, filename)
