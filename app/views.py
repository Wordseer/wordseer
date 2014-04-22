import os
import pprint

from flask import render_template, request
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import secure_filename

from app import app
import forms
from models import session, Unit, Project

def really_submitted(form):
    """ WTForms can be really finnicky when it comes to checking if a form
    has actually been submitted, so this method runs validate_on_submit()
    on the given form and checks if its "submitted" field has any data. Useful
    for pages that have two forms on them.

    :arg Form form: A form to check for submission.
    :returns boolean: True if submitted, false otherwise.
    """

    return form.validate_on_submit() and form.submitted.data

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
    try:
        session.query(Project).filter(Project.id == project_id).one()
    except NoResultFound:
        return render_template("project_not_found.html")

    upload_form = forms.DocumentUploadForm(prefix="upload")
    process_form = forms.DocumentProcessForm(prefix="process")

    if really_submitted(upload_form):
        print "UPLOAD FORM*************"
        uploaded_files = request.files.getlist("upload-uploaded_file")
        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                str(project_id), filename)
            uploaded_file.save(dest_path)
            unit = Unit(path=dest_path, project=project_id)
            unit.save()

    if really_submitted(process_form):
        print "PROCESS FORM************"
        files = request.form.getlist("process-selected_files")
        print files
        print request.form["action"]

    file_info = {}
    file_objects = session.query(Unit).filter(Unit.project == project_id).\
        filter(Unit.path != None).all()
    for file_object in file_objects:
        file_info[file_object.id] = os.path.split(file_object.path)[1]

    project = session.query(Project).filter(Project.id == project_id).one()

    return render_template("document_list.html", files=file_info,
        project=project, upload_form=upload_form, process_form=process_form)


@app.route(app.config["PROJECT_ROUTE"] + "<project_id>" +
    app.config["PROJECT_ROUTE"] + '<document_id>')
def document_show(project_id, document_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """
    return render_template("document_show.html")

@app.route(app.config["PROJECT_ROUTE"] + "<project_id>" +
    app.config["PROJECT_ROUTE"] + 'create/')
def document_create(project_id):
    """
    The create action for documents, which takes in document files, processes
    them, and creates the corresponding database records.

    NOTE: you don't need to implement the processing and database stuff since
    obviously I'm still working on that; just implement enough to confirm that
    the file was properly uploaded and would be ready for processing.
    """
    return render_template("document_create.html")

