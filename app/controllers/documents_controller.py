"""
This is the controller for pages related to documents.
"""

from app import app
from .. import models
from .. import forms
from flask import render_template
from flask import request
from werkzeug import secure_filename
import os

DOCUMENT_ROUTE = "/documents/"

def allowed_file(filename):
    return os.path.splitext(filename)[1] in app.config["ALLOWED_EXTENSIONS"]

@app.route(DOCUMENT_ROUTE)
def document_index():
    """
    The index action, which shows all files for a user.

    Eventually, this will be swapped out for the more useful page that shows all
    files in a collection.
    return render_template("documents_list.html")
    """
    file_list = []
    for unit in models.Unit.all().all():
        if unit.path:
            file_list.append(unit)
    #TODO: these paths are ugly
    return render_template("document_index.html", files=file_list)

@app.route(DOCUMENT_ROUTE + '<doc_id>')
def document_show(doc_id):
    """
    The show action, which shows details for a particular document.

    :param int doc_id: The document to retrieve details for.
    """
    return render_template("document_show.html")

@app.route(DOCUMENT_ROUTE + 'new', methods=["GET", "POST"])
def document_upload():
    """
    The new action for documents, which shows a form for uploading
    document files to process.
    """

    if request.method == "POST":
        uploaded_file = request.files["uploaded_file"]
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                filename)
            uploaded_file.save(dest_path)
            #TODO: send the user somewhere useful?
            unit = models.Unit(path=dest_path)
            unit.save()
    
    form = forms.DocumentUploadForm()
    
    return render_template('document_upload.html', form=form)

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
