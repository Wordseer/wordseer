import os
import pprint

from flask import render_template, request
from werkzeug import secure_filename

from app import app
import exceptions
import forms
from models import session, Unit, Project
import shortcuts

@app.errorhandler(exceptions.ProjectNotFoundException)
def project_not_found(error):
    return shortcuts.not_found("project")

@app.errorhandler(exceptions.DocumentNotFoundException)
def document_not_found(error):
    return shortcuts.not_found("document")

@app.errorhandler(404)
def page_not_found(error):
    return shortcuts.not_found("page")

@app.route(app.config["PROJECT_ROUTE"], methods=["GET", "POST"])
def projects():
    """
    This view handles projects. It includes a form at the top to
    create a new project, and under the form the page has a listing of
    already created projects owned by the user.
    """

    form = forms.ProjectCreateForm()

    if form.validate_on_submit():
        #TODO: is this secure? maybe not
        project = Project(name=form.name.data)
        project.save()
        os.mkdir(os.path.join(app.config["UPLOAD_DIR"], str(project.id)))

    projects = Project.all().all()

    return render_template("project_list.html", form=form, projects=projects)

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
    process_form = forms.ProcessForm(prefix="process")

    # The template needs access to the ID of each file and its filename.
    #process_form.files.choices = []
    process_form.files.choices = []
    file_objects = session.query(Unit).filter(Unit.project == project_id).\
        filter(Unit.path != None).all()
    for file_object in file_objects:
        process_form.files.choices.append((file_object.id,
            os.path.split(file_object.path)[1]))

    # First handle the actions of the upload form
    if shortcuts.really_submitted(upload_form):
        uploaded_files = request.files.getlist("upload-uploaded_file")
        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                str(project_id), filename)
            uploaded_file.save(dest_path)
            unit = Unit(path=dest_path, project=project_id)
            unit.save()

    # Then what happened with the document selection
    if shortcuts.really_submitted(process_form):
        files = request.form.getlist("process-files")
        if request.form["action"] == process_form.DELETE:
            #TODO: delete these files.
            pass
        elif request.form["action"] == process_form.PROCESS:
            #TODO: process these files.
            pass

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

    document = shortcuts.get_object_or_exception(Unit, Unit.id, document_id,
        exceptions.DocumentNotFoundException)

    filename = os.path.split(document.path)[1]
    
    return render_template("document_show.html", document=document,
        filename=filename)

@app.route(app.config["PROJECT_ROUTE"] + "<project_id>" +
    app.config["DOCUMENT_ROUTE"] + 'create/')
def document_create(project_id):
    """
    The create action for documents, which takes in document files, processes
    them, and creates the corresponding database records.

    NOTE: you don't need to implement the processing and database stuff since
    obviously I'm still working on that; just implement enough to confirm that
    the file was properly uploaded and would be ready for processing.
    """
    return render_template("document_create.html")
