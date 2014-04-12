"""
This is the controller for pages related to documents.
"""

from app import app
from .. import forms
from flask import render_template
from flask import request
from werkzeug import secure_filename

@app.route('/document/')
def document_index():
    """
    The index action, which shows all files for a user.

    Eventually, this will be swapped out for the more useful page that shows all
    files in a collection.
    return render_template("documents_list.html")
    """
    return render_template("document_index.html")

@app.route('/document/<id>')
def document_show(id):
    """
    The show action, which shows details for a particular document.

    :param int id: The document to retrieve details for.
    """
    return render_template("document_show.html")

@app.route('/document/new', methods=["GET", "POST"])
def document_upload():
    """
    The new action for documents, which shows a form for uploading
    document files to process.
    """

    if request.method == "POST":
        # do stuff
        pass
    
    form = forms.DocumentUploadForm()
    
    return render_template('document_upload.html', form=form)

@app.route('/document/create/')
def document_create():
    """
    The create action for documents, which takes in document files, processes
    them, and creates the corresponding database records.

    NOTE: you don't need to implement the processing and database stuff since
    obviously I'm still working on that; just implement enough to confirm that
    the file was properly uploaded and would be ready for processing.
    """
    return render_template("document_create.html")
