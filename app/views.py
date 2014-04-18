import os

from flask import render_template, request
from werkzeug import secure_filename

from app import app
import forms
from models import session, Unit, Project

#TODO: put these in config?
PROJECT_ROUTE = "/projects/"
DOCUMENT_ROUTE = "/documents/"

def allowed_file(filename):
    return os.path.splitext(filename)[1] in app.config["ALLOWED_EXTENSIONS"]

@app.route(PROJECT_ROUTE, methods=["GET", "POST"])
def projects():
    """
    This view handles projects. It includes a form at the top to
    create a new project, and under the form the page has a listing of
    already created projects owned by the user.
    """
    form = forms.ProjectCreateForm()

    if request.method == "POST" and form.validate():
        #TODO: is this secure? maybe not
        project = Project(name=form.name.data)
        project.save()

    projects = Project.all().all()

    return render_template("project_list.html", form=form, projects=projects)

@app.route(PROJECT_ROUTE + "<proj_id>", methods=["GET", "POST"])
def project_show(proj_id):
    """
    Show the files contained in a specific project. It also allows the user
    to upload a new document, much like projects().

    :param int proj_id: The ID of the desired project.
    """

    upload_form = forms.DocumentUploadForm(prefix="upload")
    process_form = forms.DocumentProcessForm(prefix="process")

    if request.method == "POST":
        if upload_form.validate_on_submit():
            uploaded_file = request.files["uploaded_file"]
            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                dest_path = os.path.join(app.config["UPLOAD_DIR"],
                    filename)
                uploaded_file.save(dest_path)
                #TODO: send the user somewhere useful?
                unit = Unit(path=dest_path, project=proj_id)
                unit.save()

    file_info = {}
    file_objects = session.query(Unit).filter(Unit.project == proj_id).\
        filter(Unit.path != None).all()
    for file_object in file_objects:
        file_info[file_object.id] = os.path.split(file_object.path)[1]

    project = session.query(Project).filter(Project.id == proj_id).one()

    return render_template("document_list.html", files=file_info,
        project=project, upload_form=upload_form, process_form=process_form)

#def allowed_file(filename):
    #return os.path.splitext(filename)[1] in app.config["ALLOWED_EXTENSIONS"]

#@app.route(DOCUMENT_ROUTE)
#def document_index():
    #"""
    #The index action, which shows all files for a user.

    #Eventually, this will be swapped out for the more useful page that shows
    #all files in a collection.
    #return render_template("documents_list.html")
    #"""
    #file_list = []
    #for unit in models.Unit.all().all():
        #if unit.path:
            #file_list.append(unit)
    ##TODO: these paths are ugly
    #return render_template("document_index.html", files=file_list)

@app.route(DOCUMENT_ROUTE + '<doc_id>')
def document_show(doc_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """
    return render_template("document_show.html")

#@app.route(DOCUMENT_ROUTE + 'new', methods=["GET", "POST"])
#def document_upload():
    #"""
    #The new action for documents, which shows a form for uploading
    #document files to process.
    #"""

    #if request.method == "POST":
        #uploaded_file = request.files["uploaded_file"]
        #if uploaded_file and allowed_file(uploaded_file.filename):
            #filename = secure_filename(uploaded_file.filename)
            #dest_path = os.path.join(app.config["UPLOAD_DIR"],
                #filename)
            #uploaded_file.save(dest_path)
            ##TODO: send the user somewhere useful?
            #unit = models.Unit(path=dest_path)
            #unit.save()
    
    #form = forms.DocumentUploadForm()
    
    #return render_template('document_upload.html', form=form)

@app.route(DOCUMENT_ROUTE + 'create/')
def document_create():
    """
    The create action for documents, which takes in document files, processes
    them, and creates the corresponding database records.

    NOTE: you don't need to implement the processing and database stuff since
    obviously I'm still working on that; just implement enough to confirm that
    the file was properly uploaded and would be ready for processing.
    """
    return render_template("document_create.html")

