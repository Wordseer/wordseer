"""
This file stores all the relevant forms for the web application.
"""
import os
import pdb
from flask_wtf import Form
from flask import redirect
from flask_wtf.file import FileAllowed, FileField, FileRequired
from sqlalchemy.orm.exc import NoResultFound
from flask_security.core import current_user
from wtforms.fields import StringField, HiddenField
from wtforms.validators import Required, ValidationError

from app import app
from .fields import ButtonField
from .fields import MultiCheckboxField
from .fields import MultiRadioField
from .fields import DropdownField
from ..models import Unit
from ..models import Project
from ..models import DocumentFile
from ..models import ProjectsUsers
from ..models import User
from ..models import StructureFile

class HiddenSubmitted(object):
    """A mixin to provide a hidden field called "submitted" which has a default
    value of "true".
    """

    submitted = HiddenField(default="true")

#TODO: Check if needed
def is_mappable(ids=None, units=None):
    """Validate that only one xml document is chosen to create a structure file.
    """
    doc_count = 0

    if ids:
        # Turn ids into units
        units = [DocumentFile.query.get(file_id) for file_id in ids]

    for unit in units:
        ext = os.path.splitext(unit.path)[1][1:]
        if ext in app.config["ALLOWED_EXTENSIONS"]:
            doc_count += 1

    file_path = units[0].path
    if doc_count is not 1:
        raise ValidationError("Selection must include exactly one " +
            app.config["ALLOWED_EXTENSIONS"] + " file")
    return True

def is_processable(docs=None, structure_files=None, project=None):
    """Given a list of file IDs or a Project object, determine if this
    collection of files can be processed (no more than one struc file, at least
    one xml file). You should provide either ids or units.

    :param list files: A list of file IDs to check.
    :param Project project: A Project object to check.
    :returns boolean: True if processable, raises an exception otherwise.
    """

    struc_count = 0
    doc_count = 0

    if docs or structure_files:
        doc_count = len(docs)
        struc_count = len(structure_files)

    else:
        doc_count = len(project.document_files)
        struc_count = len(project.structure_files)

    if struc_count is not 1:
        raise ValidationError("Selection must include exactly one " +
            app.config["STRUCTURE_EXTENSION"] + " file")
    if doc_count < 1:
        raise ValidationError("At least one document must be selected")
    return True

class ProcessForm(Form, HiddenSubmitted):
    """Allows the user to select which objects should be
    processed/deleted/whatever.
    """

    PROCESS = "0"
    DELETE = "-1"
    STRUCTURE = "1"

    selection = MultiCheckboxField("Select",
        coerce=int,
        choices=[])

    process_button = ButtonField("Process", name="action", value=PROCESS)
    delete_button = ButtonField("Delete", name="action", value=DELETE)
    structure_button = ButtonField("Map Structure", name="action", value=STRUCTURE)

class DocumentUploadForm(Form, HiddenSubmitted):
    """This is a form to upload files to the server. It handles both XML
    and JSON files, and is used by the document_upload view.
    """

    upload_button = ButtonField(text="Upload", name="action")

    uploaded_file = FileField("File", validators=[
        FileRequired("You must select a file"),
        FileAllowed([app.config["DOCUMENT_EXTENSION"]], "Invalid file type")
        ])

class StructureUploadForm(Form, HiddenSubmitted):
    """This is a form to upload files to the server. It handles both XML
    and JSON files, and is used by the document_upload view.
    """

    upload_button = ButtonField(text="Upload", name="action")

    uploaded_file = FileField("File", validators=[
        FileRequired("You must select a file"),
        FileAllowed([app.config["STRUCTURE_EXTENSION"]], "Invalid file type")
        ])

class DocumentProcessForm(ProcessForm):
    """A ProcessForm configured to validate selections of documents.
    """
    PROCESS = "p"
    STRUCTURE = "s"
    
    structure_file = MultiCheckboxField("Select",
        coerce=int,
        choices=[])
    
    def validate_selection(form, field):
        """If the selection is for processing, then run is_processable on the
        selected files.
        If the selection is for structure mapping, then run reirect_to_tagger
        """
        if form.process_button.data:
            if form.process_button.data[0] == form.PROCESS:
                structure_file = StructureFile.query.get(form.process_button.data[2:])
                if not structure_file:
                    raise ValidationError("This is not a structure file.")
                project = structure_file.project
           
                if project.is_processable():
                    return True
                raise ValidationError("This project can't be processed.")
            
            elif form.structure_button.data[0] == form.STRUCTURE:
                is_mappable(ids=[form.structure_button.data[2:]])
        
        elif form.process_button.data == form.DELETE:
            if len(form.structure_file.data) > 0 or len(form.selection.data) > 0:
                return True
            else:
                raise ValidationError("You must select at least one file to delete")
        

class ProjectCreateForm(Form, HiddenSubmitted):
    """Create new projects. This is simply a one-field form, requiring the
    desired name of the project.
    """

    name = StringField("Project Name", validators=[
        Required("You must provide a name")
        ])

    create_button = ButtonField("Create")

    def validate_name(form, field):
        """Make sure there are no projects with this name existing.
        """
        user_project_names = [project.name for project in current_user.projects]
        if field.data in user_project_names:
            raise ValidationError("A project with this name already exists")

class ProjectProcessForm(ProcessForm):
    """A ProcessForm configured to validate selections of projects.
    """
    DELETE = "d"
    delete_button = ButtonField("Delete", name="action")

class ConfirmDeleteForm(Form, HiddenSubmitted):
    """A form that will ask users to confirm their deletions.
    """
    DELETE = "1"
    CANCEL = "0"

    confirm_button = ButtonField(text="Yes, delete", name="action",
        value=DELETE)
    cancel_button = ButtonField(text="No, do not delete", name="action",
        value=CANCEL)

class MapDocumentForm(Form, HiddenSubmitted):
    done = 0

class ProjectPermissionsForm(Form, HiddenSubmitted):
    """List and change project permissions.
    """
    UPDATE = "0"
    DELETE = "-1"
    CREATE = "1"

    selection = MultiCheckboxField("Select",
        coerce=int,
        choices=[])

    new_collaborator = StringField("Add new user")
    possible_permissions = [(str(id), name) for id, name in
        ProjectsUsers.ROLE_DESCRIPTIONS.items()]
    create_permissions = DropdownField("Permissions", default="1",
        choices=possible_permissions)
    update_permissions = DropdownField("Permissions", default="1",
        choices=possible_permissions)
    create_button = ButtonField("Add collaborator", name="action", value=CREATE)
    update_button = ButtonField("Set permissions", name="action", value=UPDATE)
    delete_button = ButtonField("Delete", name="action", value=DELETE)

    def validate_selection(form, field):
        """Validate the selection. This only does anything if the UPDATE
        or DELETE buttons have been pressed.
        """
        action = form.create_button.data # All buttons have the same data
        if action == form.UPDATE or action == form.DELETE:
            if not field.data:
                raise ValidationError("You must make a selection")

        if ((action == form.UPDATE and
                form.update_permissions.data == str(ProjectsUsers.ROLE_USER))
                or action == form.DELETE):
            former_admins = []

            for rel_id in field.data:
                relationship = ProjectsUsers.query.get(rel_id)
                if relationship.role == ProjectsUsers.ROLE_ADMIN:
                    former_admins.append(relationship)

            if former_admins:
                project = former_admins[0].project
                all_admins = ProjectsUsers.query.filter_by(project=project,
                    role=ProjectsUsers.ROLE_ADMIN).all()
                if all_admins == former_admins:
                    raise ValidationError("At least one user must be an admin")
        return True

    def validate_new_collaborator(form, field):
        """Validate the new_collaborator field. Only does anything if CREATE
        button has been pressed.
        """
        action = form.create_button.data # All buttons have the same data
        if action == form.CREATE:
            users = User.query.all()
            user_emails = [user.email for user in users]
            existing_collaborators = [choice[1].user.id for choice in
                form.selection.choices]

            try:
                new_user = User.query.filter_by(email = field.data).one()
            except NoResultFound:
                raise ValidationError("This user does not exist. (Users must register for an account " + 
                    "before you can add them as collaborators.)")

            if new_user.id in existing_collaborators:
                raise ValidationError("This user is already on this project.")

        return True

