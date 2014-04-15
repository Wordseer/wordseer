"""
This file stores all the relevant forms for the web application.
"""

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TextField
from app import app

class DocumentUploadForm(Form):
    """This is a form to upload files to the server. It handles both XML
    and JSON files, and is used by the document_upload view.
    """

    uploaded_file = FileField("Document", validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_EXTENSIONS"])])

class ProjectCreateForm(Form):
    """
    Create new projects. This is simply a one-field form, requiring the
    desired name of the project.
    """

    name = TextField("Project Name")
    