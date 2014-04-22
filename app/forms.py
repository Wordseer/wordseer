"""
This file stores all the relevant forms for the web application.
"""

from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import TextField, HiddenField
from wtforms.validators import Required

from app import app

class HiddenSubmitted(object):
    """A mixin to provide a hidden field called "submitted" which has a default
    value of "true".
    """

    submitted = HiddenField(default="true")

class DocumentUploadForm(Form, HiddenSubmitted):
    """This is a form to upload files to the server. It handles both XML
    and JSON files, and is used by the document_upload view.
    """

    uploaded_file = FileField("File", validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_EXTENSIONS"])
        ])

class DocumentProcessForm(Form, HiddenSubmitted):
    """
    Allows the user to select which documents should be processed.
    """

    PROCESS_ALL = "0"
    DELETE_SELECTED = "-1"

class ProjectCreateForm(Form):
    """
    Create new projects. This is simply a one-field form, requiring the
    desired name of the project.
    """

    name = TextField("Project Name", validators=[
        Required()
        ])
