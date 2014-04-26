"""
This file stores all the relevant forms for the web application.
"""

from cgi import escape
import os

from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug import secure_filename
from wtforms.fields import StringField, HiddenField, Field, SelectMultipleField
from wtforms.widgets import html_params, HTMLString, ListWidget, CheckboxInput
from wtforms.validators import Required, ValidationError

from app import app
from models import Unit, session, Project

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
            units.append(session.query(Unit).\
                filter(Unit.id == file_id).one())

    for unit in units:
        # Then process the units
        ext = os.path.splitext(unit.path)[1][1:]
        if ext in app.config["STRUCTURE_EXTENSION"]:
            struc_count += 1
        else:
            doc_count += 1

    if struc_count is not 1:
        raise ValidationError("Must be exactly one structure file")
    if doc_count < 1:
        raise ValidationError("At least one document must be selected")
    return True

# TODO: might be a good idea to move the *Field and *Widget classes away

class ButtonWidget(object):
    """A widget to conveniently display buttons.
    """
    def __call__(self, field, **kwargs):
        if field.name is not None:
            kwargs.setdefault('name', field.name)
        if field.value is not None:
            kwargs.setdefault('value', field.value)
        kwargs.setdefault('type', "submit")
        return HTMLString('<button %s>%s</button>' % (
            html_params(**kwargs),
            escape(field._value())
            ))

class ButtonField(Field):
    """A field to conveniently use buttons in flask forms.
    """
    widget = ButtonWidget()

    def __init__(self, text=None, name=None, value=None, **kwargs):
        super(ButtonField, self).__init__(**kwargs)
        self.text = text
        self.value = value
        if name is not None:
            self.name = name

    def _value(self):
        return str(self.text)

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

    def add_choice(self, choice_id, choice_data):
        """Add a tuple to the choices property of the selection field. A bit
        shorter than typing out the full command.

        :param choice_id: The first item in the tuple. From a template, this
        value is reachable as the .id attribute of every item in the selection
        field.
        :param choice_data: The second item in the tuple. From a template, this
        value is reachable as the .data attribute of every item in the selection
        field.
        """

        self.choices.append((choice_id, choice_data))

    def delete_choice(self, choice_id, choice_data):
        """The reverse of add_choice: remove a choice from the choices property
        of the selection field.

        :param choice_id: The first item in the tuple. From a template, this
        value is reachable as the .id attribute of every item in the selection
        field.
        :param choice_data: The second item in the tuple. From a template, this
        value is reachable as the .data attribute of every item in the selection
        field.
        """

        self.choices.remove((choice_id, choice_data))

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
        FileAllowed(app.config["ALLOWED_EXTENSIONS"])
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
        Required()
        ])

    create_button = ButtonField("Create")

class ProjectProcessForm(ProcessForm):
    def validate_selection(form, field):
        if form.process_button.data == form.PROCESS:
            # the projects must be processable, so get a list of files
            for project_id in form.selection.data:
                project = session.query(Project).\
                    filter(Project.id == project_id).one()
                is_processable(units=project.files)
