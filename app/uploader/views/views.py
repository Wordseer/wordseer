"""
These are all the view functions for the app.
"""
import json
import logging
import os
import random
import shutil
import threading
import traceback

from string import ascii_letters, digits

from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask_security.core import current_user
from flask_security.decorators import login_required
from flask_security.utils import login_user
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import secure_filename

from .. import exceptions
from .. import forms
from .. import helpers
from .. import uploader
from app.models import *
from app import app
from app import db
from app.models import User
from app import csrf

if app.config["INSTALL_TYPE"] == "full":
    from app.preprocessor.collectionprocessor import cp_run
    from lxml import etree

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
    """Display the home page, or go direct to project list if logged in.
    """
    if current_user.is_authenticated:
        return redirect(app.config["PROJECT_ROUTE"])
    else:
        return render_template("home.html")

@uploader.route("/demo")
def start_demo():
    """Login as a restricted demo user that can view pre-loaded demo project(s). 
    User with email "demo@wordseer.berkeley.edu" must exist in the database. 
    Will log out current user immediately.
    """
    demo_user = User.query.filter(User.email=='demo@wordseer.berkeley.edu').one()
    login_user(demo_user)
    return redirect(app.config["PROJECT_ROUTE"])

@uploader.route(app.config["PROJECT_ROUTE"])
@login_required
def project_list():
    """A view for the list of a user's projects."""
    projects = []
    for project in [proj for proj in current_user.projects if not proj.deleted]:
        rel = ProjectsUsers.query.filter_by(user=current_user,
                                            project=project).one()
        projects.append({
            "name": project.name,
            "id": project.id,
            "status": project.status,
            "admin": rel.role == ProjectsUsers.ROLE_ADMIN
        })
    return render_template("project_list.html", projects=projects, 
                           create_form=forms.ProjectCreateForm())

@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>", methods=["GET", "POST"])
@login_required
def project_show(project_id):
    """A view to list documents and log messages for a single project."""
    # does user have access to the project?
    project = helpers.get_object_or_exception(Project,
                                              Project.id == project_id,
                                              exceptions.ProjectNotFoundException)
    if project not in [proj for proj in current_user.projects if not proj.deleted]:
        return app.login_manager.unauthorized()

    # what is user's permission level?
    rel = ProjectsUsers.query.filter_by(user=current_user,
                                        project=project).one()

    # initialize some form objects
    doc_form = forms.DocumentUploadForm()
    struc_form = forms.StructureUploadForm()

    # should the structure tab be active because the struc form was submitted?
    struc_active = False

    # retrieve log info
    project_errors = project.get_errors()
    project_warnings = project.get_warnings()
    project_infos = project.get_infos()

    #highest log id
    log_start = max([log.id for log in project_errors] + 
                    [log.id for log in project_warnings] + 
                    [log.id for log in project_infos] + [0])

    return render_template(
        "document_list.html", project=project, user_role=rel.role, 
        project_errors=project_errors, project_warnings=project_warnings, 
        project_infos=project_infos, doc_form=doc_form,
        struc_form=struc_form, allowed_extensions_doc=[".xml"], 
        allowed_extensions_struc=[".json"], struc_active=struc_active, log_start=log_start)

 
@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>/upload", methods=["POST"])
@login_required
def file_upload(project_id):
    """An ajax endpoint for adding files to a project
    """
    if app.config["INSTALL_TYPE"] == "full":
        # does user have access to the project?
        project = helpers.get_object_or_exception(Project,
                                                  Project.id == project_id,
                                                  exceptions.ProjectNotFoundException)
        if project not in [proj for proj in current_user.projects if not proj.deleted]:
            return app.login_manager.unauthorized()

        # what is user's permission level?
        rel = ProjectsUsers.query.filter_by(user=current_user,
                                            project=project).one()

        # handle file upload
        if rel.role != ProjectsUsers.ROLE_ADMIN:
            return app.login_manager.unauthorized()

        doc_form = forms.DocumentUploadForm()
        struc_form = forms.StructureUploadForm()

        # should the structure tab be active because the struc form was submitted?
        struc_active = False

        # For every file, check if it exists and if not then upload it to
        # the project directory and create a database record with its filename and
        # path.

        uploaded_files = request.files.getlist("uploaded_file")
        upload_errors = []
        filenames = []

        for uploaded_file in uploaded_files:
            filename = secure_filename(uploaded_file.filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                                     str(project.id), filename)
            ext = os.path.splitext(dest_path)[1][1:]
            
            # make sure file doesn't already exist
            if not os.path.isfile(dest_path):
                # Tell whether the uploaded file is a document file or a structure
                # file, and create a Document or StructureFile instance accordingly.

                if ext == app.config["STRUCTURE_EXTENSION"]:
                    if struc_form.validate():
                        uploaded_file.save(dest_path)
                        file_model = StructureFile(path=dest_path, project=project)
                        file_model.save()
                        struc_active = True
                        filenames.append({"name": filename, "type": 'struc', "id": file_model.id})

                else:
                    if doc_form.validate():
                        try:
                            # XML validation 
                            etree.fromstring(uploaded_file.read())
                            uploaded_file.seek(0)
                            
                            uploaded_file.save(dest_path)
                            file_model = DocumentFile(path=dest_path, projects=[project])
                            file_model.save()
                            filenames.append({"name": filename, "type": 'doc', "id": file_model.id})

                        except etree.XMLSyntaxError as err:
                            upload_errors.append(
                                "The file %s is not well-formed XML. Error details: %s" % (
                                    uploaded_file.filename, 
                                    json.dumps(traceback.format_exc()).replace('\\"', "'").replace('"', "")
                                )
                            )
                
            else:
                if ext == app.config["STRUCTURE_EXTENSION"]:
                    struc_form.validate()
                    upload_errors.append(
                        "A file with name " + os.path.split(dest_path)[1] + " already exists")
                    struc_active = True

                else:
                    doc_form.validate()
                    upload_errors.append(
                        "A file with name " + os.path.split(dest_path)[1] + " already exists")

        if upload_errors:
            if struc_active:
                struc_form.validate()
                struc_form.uploaded_file.errors.extend(upload_errors)
            else:
                doc_form.validate()
                doc_form.uploaded_file.errors.extend(upload_errors)

        return render_template(
            'file_upload.json', doc_form=doc_form, struc_form=struc_form, project=project,
            files=filenames)
    else:
        pass


@uploader.route(app.config["LOG_ROUTE"] + "<int:project_id>")
@login_required
def project_log(project_id):
    """An AJAX endpoint that looks for unseen preprocessor log entries and returns them.
    """
    project = helpers.get_object_or_exception(Project,
                                              Project.id == project_id,
                                              exceptions.ProjectNotFoundException)
    if project not in [proj for proj in current_user.projects if not proj.deleted]:
        return app.login_manager.unauthorized()

    start = request.args.get('start', 0)

    # retrieve log info
    project_errors = project.get_errors(start)
    project_warnings = project.get_warnings(start)
    project_infos = project.get_infos(start)

    #highest log id
    log_start = max([log.id for log in project_errors] + 
                    [log.id for log in project_warnings] + 
                    [log.id for log in project_infos] + [0])

    return render_template("processing_log.json", infos=project_infos, 
                           warnings=project_warnings, errors=project_errors, 
                           max=log_start, status=project.status)

@csrf.exempt
@uploader.route(app.config["PROCESS_ROUTE"] + "<int:project_id>", methods=["POST"])
@login_required
def project_process(project_id):
    """ An AJAX endpoint to initiate the preprocessor for the project.
    """
    if app.config["INSTALL_TYPE"] == "full":
        # does user have access to the project?
        project = helpers.get_object_or_exception(Project,
                                                  Project.id == project_id,
                                                  exceptions.ProjectNotFoundException)
        if project not in [proj for proj in current_user.projects if not proj.deleted]:
            return app.login_manager.unauthorized()

        # does user have admin permissions?
        rel = ProjectsUsers.query.filter_by(user=current_user,
                                            project=project).one()
        if rel.role != ProjectsUsers.ROLE_ADMIN:
            return app.login_manager.unauthorized()

        # retrieve the structure file and start processing
        structure_file = StructureFile.query.get(request.form["struc_id"])
        if structure_file == None or structure_file.project != project:
            return app.login_manager.unauthorized()

        # don't let a project be processed more than once
        if project.status != Project.STATUS_UNPROCESSED:
            return app.login_manager.unauthorized()

        process_files(project.path, structure_file.path, project)
        return render_template("process_project.json", project_id=project.id)
    else:
        pass


@csrf.exempt
@uploader.route(app.config["PROJECT_ROUTE"]+"<int:project_id>"+
                app.config["MAP_ROUTE"] + '<int:document_id>' + 
                app.config["SAVE_MAP"], methods=['POST'])
@login_required
def upload_structure_file(project_id, document_id):
    """
    Retireve the JSON object from te request, write it to a json file and
    save it back to the project.
    """
    if app.config["INSTALL_TYPE"] == "full":

        json_data = request.json
        dest_path = ''
        filename = ''
        counter = 0
        while os.path.isfile(dest_path) or counter == 0:
            suffix = ''
            if counter > 0:
                suffix = '_%s'%counter
            filename = json_data['filename']+"_structure"+suffix+".json"
            filename = secure_filename(filename)
            dest_path = os.path.join(app.config["UPLOAD_DIR"],
                                     str(project_id), filename)
            counter += 1

        if not os.path.isfile(dest_path):
            sfile = open(dest_path, 'w')
            sfile.write(json.dumps(json_data))
            sfile.close()
            project = Project.query.get(project_id)
            structure_file = StructureFile(path=dest_path, project=project)
            structure_file.save()

        else:
            return "A file with name " + os.path.split(dest_path)[1] + " already exists"

        return 'ok'
    else:
        pass

@uploader.route(app.config["PROJECT_ROUTE"] + "new", methods=["POST"])
@login_required
def project_create():
    """View for an AJAX endpoint that creates a new project"""
    project = Project(name=request.form["name"])
    errors = []
    current_user.add_project(project, role=ProjectsUsers.ROLE_ADMIN)
    project.path = os.path.join(app.config["UPLOAD_DIR"], str(project.id))
    project.save()
    os.mkdir(project.path)
    return render_template("create_project.json", project_id=project.id, errors=errors)

@uploader.route(app.config["PROJECT_ROUTE"] + "<int:project_id>" + 
                "/permissions", methods=["GET", "POST"])
@login_required
def project_permissions(project_id):
    """View and modify a project's permissions.
    """
    # does user have access to the project?
    project = helpers.get_object_or_exception(Project,
                                              Project.id == project_id,
                                              exceptions.ProjectNotFoundException)
    if project not in [proj for proj in current_user.projects if not proj.deleted]:
        return app.login_manager.unauthorized()

    form = forms.ProjectPermissionsForm(prefix="permissions")
    ownerships = ProjectsUsers.query.filter_by(project = project).all()

    form.selection.choices = []
    for ownership in ownerships:
        form.selection.add_choice(ownership.id, ownership)

    if request.method == "POST" and form.validate():
        selected_rels = request.form.getlist("permissions-selection")
        ownerships = [ProjectsUsers.query.get(id) for id in selected_rels]
        
        if request.form["action"] == form.DELETE:
            for ownership in ownerships:
                form.selection.delete_choice(ownership.id, ownership)
                ownership.delete()

        if request.form["action"] == form.UPDATE:
            role = int(request.form["permissions-update_permissions"])
            for ownership in ownerships:
                ownership.role = role
                ownership.save(False)
            db.session.commit()

        if request.form["action"] == form.CREATE:
            email = request.form["permissions-new_collaborator"]
            role = int(request.form["permissions-create_permissions"])
            user = User.query.filter(User.email == email).one()
            rel = user.add_project(project=project, role=role)
            form.selection.add_choice(rel.id, rel)
            

    return render_template("project_permissions.html", project=project, form=form)


@csrf.exempt
@uploader.route(app.config["DELETE_ROUTE"], methods=["POST"])
@login_required
def delete_obj():
    """Given a Unit or Project object, delete their files and database records.
    """
    # retrieve relevant variables from request params
    project_id = request.form["project_id"]
    obj_type = request.form["obj_type"]
    obj_id = request.form["obj_id"]
    
    # does user have access to project?
    project = helpers.get_object_or_exception(Project,
                                              Project.id == project_id,
                                              exceptions.ProjectNotFoundException)
    if project not in [proj for proj in current_user.projects if not proj.deleted]:
        return app.login_manager.unauthorized()

    # does user have admin permissions?
    rel = ProjectsUsers.query.filter_by(user=current_user,
                                        project=project).one()
    if rel.role != ProjectsUsers.ROLE_ADMIN:
        return app.login_manager.unauthorized()

    # figure out what they want to delete, and delete it
    if obj_type == "project":
        obj = Project.query.get(obj_id)
        
        # just flag for deletion instead of actually deleting
        obj.deleted = True
        obj.save()
        # TODO: implement garbage collection
        return render_template("delete_obj.json", obj_type=obj_type, obj_id=obj_id)

    elif obj_type == "doc":
        obj = DocumentFile.query.get(obj_id)
    elif obj_type == "struc":
        obj = StructureFile.query.get(obj_id)

    obj.delete()

    if os.path.isdir(obj.path):
        shutil.rmtree(obj.path)
    else:
        os.remove(obj.path)

    return render_template("delete_obj.json", obj_type=obj_type, obj_id=obj_id)

@csrf.exempt
@uploader.route(app.config["PROJECT_ROUTE"]+"<int:project_id>"+
                app.config["MAP_ROUTE"] + '<int:document_file_id>')
@login_required
def document_map(project_id, document_file_id):
    """
    The map xml action, which is used create a structure map file for document.

    :param int doc_id: The document to retrieve details for.
    """
    try:
        document = DocumentFile.query.get(document_file_id)
    except TypeError:
        return app.login_manager.unauthorized()

    access_granted = current_user.has_document_file(
        DocumentFile.query.get(document_file_id))

    # Test if this user can see it
    if not access_granted:
        return app.login_manager.unauthorized()

    filename = os.path.split(document.path)[1]
    project = Project.query.get(project_id)
    map_document = forms.MapDocumentForm()
    return render_template(
        "document_map.html",
        document=document,
        project=project,
        filename=filename,
        map_document=map_document
    )

@csrf.exempt
@uploader.route(app.config["UPLOAD_ROUTE"] + "<filetype>/<int:file_id>")
@login_required
def get_file(filetype, file_id):
    """If the user has permission to view this file, then return it.
    """

    if filetype == "doc":
        document_file = DocumentFile.query.get(file_id)
        try:
            access_granted = current_user.has_document_file(document_file)
        except TypeError:
            return app.login_manager.unauthorized()
    elif filetype == "struc":
        document_file = StructureFile.query.get(file_id)
        try:
            access_granted = current_user.has_structure_file(document_file)
        except TypeError:
            return app.login_manager.unauthorized()

    # Test if this user can see it
    if not access_granted:
        return app.login_manager.unauthorized()
    directory, filename = os.path.split(document_file.path)

    return send_from_directory(directory, filename)


def process_files(collection_dir, structure_file, project):
    """Process a list of files using the preprocessor. This must be a valid list
    of files or bad things will happen - exactly one structure file, several
    document files.
    """
    logger = logging.getLogger()
    if app.config["INSTALL_TYPE"] == "partial":
        logger.info("Not processing as per config.")
        return
    project.status = Project.STATUS_PREPROCESSING
    project.save()
    args = (collection_dir, structure_file, app.config["DOCUMENT_EXTENSION"],
            project.id)
    preprocessing_process = threading.Thread(target=cp_run, args=args)
    preprocessing_process.start()
