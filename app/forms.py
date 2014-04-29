"""
This file stores all the relevant forms for the web application.
"""

import os

from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug import secure_filename
from wtforms.fields import StringField, HiddenField
from wtforms.validators import Required, ValidationError

from app import app
from fields import ButtonField, MultiCheckboxField
from models import Unit, Project
from widgets import ButtonWidget

class HiddenSubmitted(object):
    """A mixin to provide a hidden field called "submitted" which has a default
    value of "true".
    """

    submitted = HiddenField(default="true")

def is_processable(ids=None, units=None):
    """Given a list of file IDs or Unit objects, determine if this collection of
    files can be processed (no more than one struc file, at least one xml file).
    You should provide either ids or units.

    :param list files: A list of file IDs to check.
    :param list units: A list of Unit objects to check.
    :returns boolean: True if processable, raises an exception otherwise.
    """

    #TODO: could be a cleaner way to write this

    struc_count = 0
    doc_count = 0

    if ids:
        # Turn ids into units
        units = []
        for file_id in ids:
            units.append(Unit.filter(Unit.id == file_id).one())

    for unit in units:
        # Then process the units
        ext = os.path.splitext(unit.path)[1][1:]
        if ext in app.config["STRUCTURE_EXTENSION"]:
            struc_count += 1
        else:
            doc_count += 1

    if struc_count is not 1:
        raise ValidationError("Selection must include exactly one " +
            app.config["STRUCTURE_EXTENSION"] + " file")
    if doc_count < 1:
        raise ValidationError("At least one document must be selected")
    return True

class ProcessForm(Form, HiddenSubmitted):
    """
    Allows the user to select which objects should be
    processed/deleted/whatever.
    """

    PROCESS = "0"
    DELETE = "-1"

    selection = MultiCheckboxField("Select",
        coerce=int,
        validators=[
            Required("You must select at least one item from the table.")
        ],
        choices=[])
    process_button = ButtonField("Process", name="action", value=PROCESS)
    delete_button = ButtonField("Delete",  name="action", value=DELETE)

class DocumentUploadForm(Form, HiddenSubmitted):
    """This is a form to upload files to the server. It handles both XML
    and JSON files, and is used by the document_upload view.
    """

    upload_button = ButtonField(text="Upload", name="action")

    uploaded_file = FileField("File", validators=[
        FileRequired("You must select a file"),
        FileAllowed(app.config["ALLOWED_EXTENSIONS"], "Invalid file type")
        ])

class DocumentProcessForm(ProcessForm):
    def validate_selection(form, field):
        if form.process_button.data == form.PROCESS:
            is_processable(ids=form.selection.data)

class ProjectCreateForm(Form, HiddenSubmitted):
    """
    Create new projects. This is simply a one-field form, requiring the
    desired name of the project.
    """

    name = StringField("Project Name", validators=[
        Required("You must provide a name")
        ])

    create_button = ButtonField("Create")

    def validate_name(form, field):
        if Project.filter(Project.name == field.data).count() > 0:
            raise ValidationError("A project with this name already exists")

class ProjectProcessForm(ProcessForm):
    def validate_selection(form, field):
        if form.process_button.data == form.PROCESS:
            # the projects must be processable, so get a list of files
            for project_id in form.selection.data:
                project = Project.filter(Project.id == project_id).one()
                is_processable(units=project.files)
