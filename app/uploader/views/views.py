"""
These are all the view functions for the app.
"""
import os
import threading
import shutil
import random
import json
from string import ascii_letters, digits
from cStringIO import StringIO
import logging

from flask import config
from flask import redirect, url_for
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask_security.core import current_user
from flask_security.decorators import login_required
from flask.views import View
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import secure_filename

from .. import exceptions
from .. import forms
from .. import helpers
from .. import uploader
from ...models import Document
from ...models import DocumentFile
from ...models import Project
from ...models import StructureFile
from ...models import Unit
from ...models import User
from ...models import ProjectsUsers
from app import app
from app import db
from app.models import User
from app import csrf

if app.config["INSTALL_TYPE"] == "full":
    from app.preprocessor.collectionprocessor import cp_run

def generate_form_token():
    """Sets a token to prevent double posts."""
    if '_form_token' not in session:
        form_token = ''.join(
            [random.choice(ascii_letters+digits) for i in range(32)])
        session['_form_token'] = form_token
    return session['_form_token']

@uploader.before_request
def check_form_token():
    """Checks for a valid form token in POST requests."""
    if request.method == 'POST':
        token = session.pop('_form_token', None)
        if not token or token != request.form.get('_form_token'):
            redirect(request.url)

@uploader.route("/")
def home():
    """Display the home page.
    """
    if current_user.is_authenticated():
        return redirect(app.config["PROJECT_ROUTE"])
    else:
        return render_template("home.html")

@uploader.route(app.config["PROJECT_ROUTE"])
def project_list():
    """A view for the list of a user's projects."""
    if current_user.is_authenticated():
        projects = []
        for project in current_user.projects:
            rel = ProjectsUsers.query.filter_by(user=current_user,
            project=project).one()
            projects.append({
                "name": project.name,
                "id": project.id,
                "status": project.status,
                "admin": rel.role == ProjectsUsers.ROLE_ADMIN
            })
        return render_template("project_list.html", projects=projects, create_form=forms.ProjectCreateForm())
    else:
        return redirect("/")

@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>")
def project_show(project_id):
    """A view to list documents and log messages for a single project."""
    if current_user.is_authenticated():
        # does user have access to the project?
        project = helpers.get_object_or_exception(Project,
            Project.id == project_id,
            exceptions.ProjectNotFoundException)
        if project not in current_user.projects:
            return #500 error

        # what is user's permission level?
        rel = ProjectsUsers.query.filter_by(user=current_user,
            project=project).one()

        # retrieve log info
        project_errors = project.get_errors()
        project_warnings = project.get_warnings()
        project_infos = project.get_infos()

        return render_template("document_list.html", project=project, user_role=rel.role, 
            project_errors=project_errors, project_warnings=project_warnings, 
            project_infos=project_infos)
    else:
        return redirect("/")

@uploader.route(app.config["PROJECT_ROUTE"] + "new", methods=["POST"])
def project_create():
    """View for an AJAX endpoint that creates a new project"""
    if current_user.is_authenticated():
        project = Project(name=request.form["name"])
        errors = []
        current_user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
        project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
        project.save()
        os.mkdir(project.path)
        return render_template("create_project.json", project_id=project.id, errors=errors)

@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/permissions")
def project_permissions():
    pass

@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/document/")
def document_show():
    pass

@uploader.route(app.config["DELETE_ROUTE"], methods=["POST"])
def delete_obj():
    """Given a Unit or Project object, delete their files and database records.
    """
    if current_user.is_authenticated():

        # retrieve relevant variables from request params
        project_id = request.form["project_id"]
        obj_type = request.form["obj_type"]
        obj_id = request.form["obj_id"]
        
        # does user have access to project?
        project = helpers.get_object_or_exception(Project,
            Project.id == project_id,
            exceptions.ProjectNotFoundException)
        if project not in current_user.projects:
            return #500 error

        # does user have admin permissions?
        rel = ProjectsUsers.query.filter_by(user=current_user,
            project=project).one()
        if rel.role != ProjectsUsers.ROLE_ADMIN:
            return #500 error

        # figure out what they want to delete, and delete it
        if obj_type == "project":
            obj = Project.query.get(obj_id)

        if os.path.isdir(obj.path):
            shutil.rmtree(obj.path)
            for document_file in obj.document_files:
                #TODO: can't we cascade this?
                document_file.delete()
            db.session.commit()
        else:
            os.remove(obj.path)

        # if isinstance(obj, StructureFile):
        #     self.process_form.structure_file.delete_choice(obj.id, data)

        # else:
        #     self.process_form.selection.delete_choice(obj.id, data)

        obj.delete()

        return render_template("delete_obj.json", obj_type=obj_type, obj_id=obj_id)

    else:
        return #500 error

# class CLPDView(View):
#     """This is a pluggable view to handle CLPD (Create, List, Process, Delete)
#     views.

#     In this application, we have two CLPD views which are in many ways very
#     similar: the project listing and the document listing. With this view,
#     we can reduce the redundancy.
#     """

#     #TODO : facilitate delete

#     decorators = [login_required]
#     methods = ["GET", "POST"]

#     def __init__(self, template, create_form, process_form,
#         confirm_delete_form):
#         """Initializes a CLPD view. kwargs are data passed to the view in
#         general.

#         :arg str template: The name of the template to use for rendering.
#         :arg Form create_form: The form to use for creation.
#         :arg Form process_form: The form to use for listing, processing,
#         and deleting.
#         :arg Form confirm_delete_form: The form to use for confirming a
#         deletion.
#         """
#         self.template = template
#         self.create_form = create_form(prefix="create")
#         self.process_form = process_form(prefix="process")
#         self.confirm_delete_form = confirm_delete_form(prefix="confirm_delete")

#         self.template_kwargs = {}

#     # TODO: this method does more than delete the object so its name should
#     # reflect that
#     def delete_object(self, obj, data):
#         """Given a Unit or Project object, delete their files,
#         database records, and entries in the process form's choices.
#         :arg obj: A DocumentFile or Project objects.
#         :arg data: The second part of the tuple in the process form, the first
#         item being the object's id.
#         """
#         if os.path.isdir(obj.path):
#             shutil.rmtree(obj.path)
#             for document_file in obj.document_files:
#                 #TODO: can't we cascade this?
#                 document_file.delete()
#             db.session.commit()
#         else:
#             os.remove(obj.path)

#         if isinstance(obj, StructureFile):
#             self.process_form.structure_file.delete_choice(obj.id, data)

#         else:
#             self.process_form.selection.delete_choice(obj.id, data)

#         obj.delete()

#     def set_choices(self, **kwargs):
#         """Set the appropriate choices for the list view.
#         """
#         raise NotImplementedError()

#     def handle_create(self, **kwargs):
#         """Perform actions necessary for the create_form.
#         """
#         raise NotImplementedError()

#     def handle_process(self, **kwargs):
#         """Perform actions necessary for the process_form.
#         """
#         raise NotImplementedError()

#     def reset_fields(self):
#         """If necessary, reset fields.
#         """
#         self.create_form.submitted.data = "true"
#         self.process_form.submitted.data = "true"

#     def pre_tests(self, **kwargs):
#         """If necessary, run checks before continuing with the view logic.

#         If this function returns anything, then the return value will be the
#         returned response rather than the template. This is useful for
#         authorization checks.
#         """
#         pass

#     def dispatch_request(self, **kwargs):
#         """Render the template with the required data. kwargs are data
#         passed to the URL.
#         if the map request button is clicked and valid, redirect to the mapping page
#         """
#         not_authorized = self.pre_tests(**kwargs)

#         if not_authorized:
#             return not_authorized

#         to_redirect = 0

#         self.set_choices(**kwargs)

#         if helpers.really_submitted(self.create_form):
#             self.handle_create(**kwargs)

#         elif helpers.really_submitted(self.process_form):
#             to_redirect = self.handle_process(**kwargs)

#         #TODO: maybe not the cleanest way to do it!!
#         if to_redirect == 0 or to_redirect is None:
#             self.reset_fields()

#             return render_template(self.template,
#                 create_form=self.create_form,
#                 process_form=self.process_form,
#                 **self.template_kwargs)
#         else:
#             return redirect(to_redirect)

# class CreateProjectView(CLPDView):
#     def __init__(self):
#         super(CreateProjectView, self).__init__("create_project.json",
#             forms.ProjectCreateForm, forms.ProjectProcessForm,
#             forms.ConfirmDeleteForm)

#     def set_choices(self, **kwargs):
#         pass

#     def handle_process(self, **kwargs):
#         pass

#     def handle_create(self, **kwargs):
#         """Created projects are created in the database with a name, a user,
#         and a path. Their path is also created.
#         """
#         project = Project(name=request.form["name"])
#         current_user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
#         project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
#         project.save()
#         os.mkdir(project.path)
#         self.template_kwargs["project_id"] = project.id

# uploader.add_url_rule(app.config["PROJECT_ROUTE"] + "new", 
#     view_func=CreateProjectView.as_view("project_create"))


# class ProjectsCLPD(CLPDView):
#     """A CLPD view for the list of a user's projects.
#     """
#     def __init__(self):
#         super(ProjectsCLPD, self).__init__("project_list.html",
#             forms.ProjectCreateForm, forms.ProjectProcessForm,
#             forms.ConfirmDeleteForm)

#         self.template_kwargs["statuses"] = [p.status for p in current_user.projects]

#     def set_choices(self, **kwargs):
#         """Every choice is in the form of (project.id, project.name).
#         """
#         self.process_form.selection.choices = []
#         for project in current_user.projects:
#             self.process_form.selection.add_choice(project.id, project.name)

#     def handle_create(self, **kwargs):
#         """Created projects are created in the database with a name, a user,
#         and a path. Their path is also created.
#         """
#         project = Project(
#             name=self.create_form.name.data)
#         current_user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
#         project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
#         project.save()
#         os.mkdir(project.path)
#         self.process_form.selection.add_choice(project.id, project.name)

#     def handle_process(self, **kwargs):
#         """For deletion, delete call delete_object on the object and delete
#         its path. For processing, send the project to the processor.
#         """
#         selected_project = Project.query.get(request.form["action"][2:])
#         if request.form["action"][0] ==  self.process_form.DELETE:
#             rel = ProjectsUsers.query.filter_by(user=current_user,
#                 project=selected_project).one()

#             if rel.role < ProjectsUsers.ROLE_ADMIN:
#                 self.process_form.selection.errors.append("Not authorized"
#                     " to delete " + selected_project.name)
#                 return

#             self.delete_object(selected_project, selected_project.name)

# uploader.add_url_rule(app.config["PROJECT_ROUTE"],
#     view_func=ProjectsCLPD.as_view("projects"))

# #TODO: rename this?
# # NOTE: Is this not basically document handling? DocumentCLPD would be fine
# # although I really don't like CLPD at the end; can we just call these views
# # ProjectsView and DocumentsView? (plural because they handle multiple objects)
# class ProjectCLPD(CLPDView):
#     """CLPD view for listing files in a project.
#     """
#     def __init__(self):
#         super(ProjectCLPD, self).__init__("document_list.html",
#             forms.DocumentUploadForm, forms.DocumentProcessForm,
#             forms.ConfirmDeleteForm)
#         self.template_kwargs["allowed_extensions"] = \
#             [ "." + ext for ext in app.config["ALLOWED_EXTENSIONS"]]

#     def pre_tests(self, **kwargs):
#         """Make sure this project exists and make sure that this user can see
#         the project.
#         """
#         self.project = helpers.get_object_or_exception(Project,
#             Project.id == kwargs["project_id"],
#             exceptions.ProjectNotFoundException)
#             # NOTE: handle access to nonexistent objects globally

#         if self.project not in current_user.projects:
#             return app.login_manager.unauthorized()

#         self.template_kwargs["project"] = self.project
#         self.template_kwargs["project_errors"] = self.project.get_errors()
#         self.template_kwargs["project_warnings"] = self.project.get_warnings()
#         self.template_kwargs["project_infos"] = self.project.get_infos()

#         self.rel = ProjectsUsers.query.filter_by(user=current_user,
#             project=self.project).one()
#         self.template_kwargs["user_role"] = self.rel.role

#     def set_choices(self, **kwargs):
#         """The template needs the choices in the form of (id, filename).
#         """
#         file_objects = self.project.document_files
#         self.process_form.selection.choices = []
#         self.process_form.structure_file.choices = []

#         for file_object in file_objects:
#             self.process_form.selection.add_choice(file_object.id,
#                 os.path.split(file_object.path)[1])

#         for structure_file in self.project.structure_files:
#             self.process_form.structure_file.add_choice(structure_file.id,
#                 os.path.split(structure_file.path)[1])

#     def handle_create(self, **kwargs):
#         """For every file, check if it exists and if not then upload it to
#         the project directory and create a database record with its filename and
#         path.
#         """
#         if self.rel.role < ProjectsUsers.ROLE_ADMIN:
#             self.create_form.uploaded_file.errors.append("You can't do that.")
#             return
#         uploaded_files = request.files.getlist("create-uploaded_file")
#         for uploaded_file in uploaded_files:
#             filename = secure_filename(uploaded_file.filename)
#             dest_path = os.path.join(app.config["UPLOAD_DIR"],
#                 str(self.project.id), filename)
#             # TODO: this checks if the file exists, but can we do this
#             # inside the form?
#             if not os.path.isfile(dest_path):
#                 self.upload_file(uploaded_file, dest_path)
#             else:
#                 self.create_form.uploaded_file.errors.append("A file with "
#                     "name " + os.path.split(dest_path)[1] + " already exists")

#     def upload_file(self, uploaded_file, dest_path):
#         """Tell whether the uploaded file is a document file or a structure
#         file, and create a Document or StructureFile instance accordingly.

#         This does not validate anything.

#         Arguments:
#             uploaded_file (file): The file that's been uploaded.
#             dest_path (str): The destination for uploading.
#         """
#         uploaded_file.save(dest_path)
#         ext = os.path.splitext(dest_path)[1][1:]

#         if ext == app.config["STRUCTURE_EXTENSION"]:
#             file_model = StructureFile(path=dest_path, project=self.project)
#             file_model.save()
#             self.process_form.structure_file.add_choice(file_model.id,
#                 os.path.split(dest_path)[1])

#         else:
#             file_model = DocumentFile(path=dest_path, projects=[self.project])
#             file_model.save()
#             self.process_form.selection.add_choice(file_model.id,
#                 os.path.split(dest_path)[1])

#     def handle_process(self, **kwargs):
#         """If deleting, delete every database record and file. If processing,
#         then send files to the processor.
#         """
#         if self.rel.role < ProjectsUsers.ROLE_ADMIN:
#             self.process_form.selection.errors.append("You can't do that.")
#             return

#         if request.form["action"] == self.process_form.DELETE:
#             # Delete every selected file, its database record, and item in
#             # the listing
#             files = request.form.getlist("process-selection")
#             structure_file_ids = request.form.getlist("process-structure_file")
#             file_objects = [DocumentFile.query.get(id) for id in files]
#             structure_files = [StructureFile.query.get(id) for id in structure_file_ids]
#             delete = file_objects + structure_files
#             for file_object in delete:
#                 file_name = os.path.split(file_object.path)[1]
#                 self.delete_object(file_object, file_name)

#         if request.form["action"][0] == self.process_form.PROCESS:
#             # Make sure the user isn't doing something freaky
#             structure_file = StructureFile.query.get(request.form["action"][2:])
#             if structure_file.project != self.project:
#                 self.process_form.structure_file.errors.append("You can't do that.")

#             process_files(self.project.path, structure_file.path,
#                 self.project)

#         elif request.form["action"][0] == self.process_form.STRUCTURE:
#             # return the URL for structure mapping
#             file_id = request.form["action"][2:]
#             file_model = DocumentFile.query.get(file_id)
#             file_name = os.path.split(file_model.path)[1]
#             url = url_for('uploader.document_map',
#                 document_file_id=int(float(file_id)), **kwargs)
#             return url

#         return 0

# uploader.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>",
#     view_func=ProjectCLPD.as_view("project_show"))

# class ProjectPermissions(View):
#     """View and modify a project's permissions.
#     """
#     decorators = [login_required]
#     methods = ["GET", "POST"]
#     def __init__(self):
#         self.form = forms.ProjectPermissionsForm(prefix="permissions")

#     def handle_form(self):
#         """Handle the form actions.
#         """
#         selected_rels = request.form.getlist("permissions-selection")
#         ownerships = [ProjectsUsers.query.get(id) for id in selected_rels]
#         if request.form["action"] == self.form.DELETE:
#             for ownership in ownerships:
#                 self.form.selection.delete_choice(ownership.id, ownership)
#                 ownership.delete()

#         if request.form["action"] == self.form.UPDATE:
#             role = int(request.form["permissions-update_permissions"])
#             for ownership in ownerships:
#                 ownership.role = role
#                 ownership.save(False)
#             db.session.commit()

#         if request.form["action"] == self.form.CREATE:
#             email = request.form["permissions-new_collaborator"]
#             role = int(request.form["permissions-create_permissions"])
#             user = User.query.filter(User.email == email).one()
#             rel = user.add_project(project=self.project, role=role)
#             self.form.selection.add_choice(rel.id, rel)


#     def set_choices(self):
#         """Get the possible choices.
#         """
#         ownerships = ProjectsUsers.query.filter_by(project = self.project).all()

#         self.form.selection.choices = []
#         for ownership in ownerships:
#             self.form.selection.add_choice(ownership.id, ownership)

#     def dispatch_request(self, project_id):
#         """Render the template with the correct data.
#         """
#         self.project = Project.query.get(project_id)
#         if (not self.project or
#                 self.project not in current_user.projects or
#                 ProjectsUsers.query.filter_by(project = self.project).\
#                     filter_by(user = current_user).one().role is not
#                     ProjectsUsers.ROLE_ADMIN):
#             return app.login_manager.unauthorized()
#         self.set_choices()
#         if helpers.really_submitted(self.form):
#             self.handle_form()

#         return render_template("project_permissions.html",
#             project=self.project,
#             form=self.form)

# uploader.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/permissions",
#     view_func=ProjectPermissions.as_view("project_permissions"))


# @uploader.route(app.config["DOCUMENT_ROUTE"] + '<int:document_file_id>')
# @login_required
# def document_show(document_file_id):
#     """The show action, which shows details for a particular DocumentFile.

#     :param int document_file_id: The DocumentFile to retrieve details for.
#     """
#     #TODO: good spot for a helper
#     #document = helpers.get_object_or_exception(Unit,
#     #   Unit.id == document_id, exceptions.DocumentNotFoundException)
#     try:
#         document_file = DocumentFile.query.get(document_file_id)
#     except TypeError:
#         return app.login_manager.unauthorized()

#     access_granted = current_user.has_document_file(document_file)

#     # Test if this user can see it
#     if not access_granted:
#         return app.login_manager.unauthorized()

#     filename = os.path.split(document_file.path)[1]
#     #TODO: move to objects

#     return render_template("document_show.html",
#         document_file=document_file,
#         filename=filename)

# @csrf.exempt
# @uploader.route(app.config["PROJECT_ROUTE"]+"<int:project_id>"+
#     app.config["MAP_ROUTE"] + '<int:document_file_id>')
# @login_required
# def document_map(project_id, document_file_id):
#     """
#     The map xml action, which is used create a sturctuve file map for document.

#     :param int doc_id: The document to retrieve details for.
#     """
#     try:
#         document = DocumentFile.query.get(document_file_id)
#     except TypeError:
#         return app.login_manager.unauthorized()

#     access_granted = current_user.has_document_file(
#         DocumentFile.query.get(document_file_id))

#     # Test if this user can see it
#     if not access_granted:
#         return app.login_manager.unauthorized()

#     filename = os.path.split(document.path)[1]
#     project = Project.query.get(project_id)
#     map_document = forms.MapDocumentForm()
#     return render_template("document_map.html",
#         document=document,
#         project=project,
#         filename=filename,
#         map_document = map_document,
#         document_url="%s%s"%(app.config["UPLOAD_ROUTE"],document.id))

# @uploader.route(app.config["UPLOAD_ROUTE"] + "<int:file_id>")
# @login_required
# def get_file(file_id):
#     """If the user has permission to view this file, then return it.
#     """

#     document_file = DocumentFile.query.get(file_id)
#     try:
#         access_granted = current_user.has_document_file(document_file)
#     except TypeError:
#         return app.login_manager.unauthorized()
#     # TODO: clearer error handling

#     # Test if this user can see it
#     if not access_granted:
#         return app.login_manager.unauthorized()
#     directory, filename = os.path.split(document_file.path)

#     return send_from_directory(directory, filename)

# def process_files(collection_dir, structure_file, project):
#     """Process a list of files using the preprocessor. This must be a valid list
#     of files or bad things will happen - exactly one structure file, several
#     document files.
#     """
#     project.status = Project.STATUS_PREPROCESSING
#     logger = logging.getLogger()
#     if app.config["INSTALL_TYPE"] == "partial":
#         logger.info("Not processing as per config.")
#         return
#     args = (collection_dir, structure_file, app.config["DOCUMENT_EXTENSION"],
#         project.id)
#     preprocessing_process = threading.Thread(target=cp_run, args=args)
#     preprocessing_process.start()

# @csrf.exempt
# @uploader.route(app.config["PROJECT_ROUTE"]+"<int:project_id>"+
#     app.config["MAP_ROUTE"] + '<int:document_id>'+app.config["SAVE_MAP"], methods=['POST'])
# @login_required
# def upload_structure_file( project_id, document_id):
#     """
#     Retireve the JSON object from te request, write it to a json file and
#     save it back to the project.
#     """
#     json_data = request.json
#     dest_path = ''
#     filename=''
#     counter = 0
#     while os.path.isfile(dest_path) or counter==0:
#         suffix = ''
#         if counter >0:
#             suffix='_%s'%counter
#         filename = json_data['filename']+"_structure"+suffix+".json"
#         filename = secure_filename(filename)
#         dest_path = os.path.join(app.config["UPLOAD_DIR"],
#             str(project_id), filename)
#         counter+=1

#     # TODO: this checks if the file exists, but can we do this
#     # inside the form?
#     if not os.path.isfile(dest_path):
#         f = open(dest_path, 'w');
#         f.write(json.dumps(json_data))
#         f.close();
#         project = Project.query.get(project_id)
#         structure_file = StructureFile(path=dest_path, project=project)
#         structure_file.save()

#     else:
#         return "A file with name " + os.path.split(dest_path)[1] + " already exists"

#     return 'ok'

