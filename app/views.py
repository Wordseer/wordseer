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

@app.route(app.config["PROJECT_ROUTE"], methods=["GET", "POST"])
def projects():
    """
    This view handles projects. It includes a form at the top to
    create a new project, and under the form the page has a listing of
    already created projects owned by the user.
    """

    create_form = forms.ProjectCreateForm(prefix="create")
    process_form = forms.ProjectProcessForm(prefix="process")

    process_form.selection.choices = []
    for project in Project.all().all():
        process_form.add_choice(project.id, project.name)

    if shortcuts.really_submitted(create_form):
        #TODO: is this secure? maybe not
        project = Project(name=create_form.name.data)
        project.save()
        os.mkdir(os.path.join(app.config["UPLOAD_DIR"], str(project.id)))
        process_form.add_choice(project.id, project.name)


    create_form.submitted.data == "true"
    process_form.submitted.data == "true"

    return render_template("project_list.html",
        create_form=create_form,
        process_form=process_form,
        projects=projects)

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
    process_form.selection.choices = []
    file_objects = session.query(Unit).filter(Unit.project_id == project_id).\
        filter(Unit.path != None).all()
    for file_object in file_objects:
        process_form.add_choice(file_object.id,
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
                process_form.add_choice(unit.id, os.path.split(dest_path)[1])
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
                process_form.delete_choice(int(file_id), file_name)

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
