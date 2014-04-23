"""
This file stores all the relevant forms for the web application.
"""

from cgi import escape

from flask_wtf import Form
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms.fields import StringField, HiddenField, Field, SelectMultipleField
from wtforms.widgets import html_params, HTMLString, ListWidget, CheckboxInput
from wtforms.validators import Required

from app import app

class HiddenSubmitted(object):
    """A mixin to provide a hidden field called "submitted" which has a default
    value of "true".
    """

    submitted = HiddenField(default="true")

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

class DocumentUploadForm(Form, HiddenSubmitted):
    """This is a form to upload files to the server. It handles both XML
    and JSON files, and is used by the document_upload view.
    """

    upload_button = ButtonField(text="Upload", name="action")

    uploaded_file = FileField("File", validators=[
        FileRequired(),
        FileAllowed(app.config["ALLOWED_EXTENSIONS"])
        ])

class DocumentProcessForm(Form, HiddenSubmitted):
    """
    Allows the user to select which documents should be processed.
    """

    PROCESS = "0"
    DELETE = "-1"

    files = MultiCheckboxField("Select")
    process_button = ButtonField("Process", name="action", value=PROCESS)
    delete_button = ButtonField("Delete",  name="action", value=DELETE)

    

class ProjectCreateForm(Form):
    """
    Create new projects. This is simply a one-field form, requiring the
    desired name of the project.
    """

    name = StringField("Project Name", validators=[
        Required()
        ])

    create_button = ButtonField("Create")
