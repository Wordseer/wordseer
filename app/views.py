import os
import pprint

from flask import render_template, request
from werkzeug import secure_filename

from app import app
import forms
from models import session, Unit, Project

#TODO: put these in config?
PROJECT_ROUTE = "/projects/"
DOCUMENT_ROUTE = "/documents/"

@app.route(PROJECT_ROUTE, methods=["GET", "POST"])
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

    projects = Project.all().all()

    return render_template("project_list.html", form=form, projects=projects)

@app.route(PROJECT_ROUTE + "<project_id>", methods=["GET", "POST"])
def project_show(project_id):
    """
    Show the files contained in a specific project. It also allows the user
    to upload a new document, much like projects().

    :param int project_id: The ID of the desired project.
    """

    upload_form = forms.DocumentUploadForm(prefix="upload")
    process_form = forms.DocumentProcessForm(prefix="process")

    if request.method == "POST":
        if upload_form.validate():
            uploaded_file = request.files["upload-uploaded_file"]
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                filename)
            uploaded_file.save(dest_path)
            unit = Unit(path=dest_path, project=project_id)
            unit.save()
        #TODO: check other form as well
        #TODO: multiple file upload

    file_info = {}
    file_objects = session.query(Unit).filter(Unit.project == project_id).\
        filter(Unit.path != None).all()
    for file_object in file_objects:
        file_info[file_object.id] = os.path.split(file_object.path)[1]

    project = session.query(Project).filter(Project.id == project_id).one()

    return render_template("document_list.html", files=file_info,
        project=project, upload_form=upload_form, process_form=process_form)


@app.route(PROJECT_ROUTE + "<project_id>" + DOCUMENT_ROUTE + '<document_id>')
def document_show(project_id, document_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """
    return render_template("document_show.html")

@app.route(PROJECT_ROUTE + "<project_id>" + DOCUMENT_ROUTE + 'create/')
def document_create(project_id):
    """
    The create action for documents, which takes in document files, processes
    them, and creates the corresponding database records.

    NOTE: you don't need to implement the processing and database stuff since
    obviously I'm still working on that; just implement enough to confirm that
    the file was properly uploaded and would be ready for processing.
    """
    return render_template("document_create.html")
