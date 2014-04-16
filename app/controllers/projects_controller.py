from flask import render_template, request

from app import app
from .. import models
from .. import forms

PROJECT_ROUTE = "/projects/"

@app.route(PROJECT_ROUTE, methods=["GET", "POST"])
def projects():
    """
    This controller handles projects. It includes a form at the top to
    create a new project, and under the form the page has a listing of
    already created projects owned by the user.
    """
    form = forms.ProjectCreateForm()

    if request.method == "POST" and form.validate():
        #TODO: is this secure? maybe not
        project = models.Project(name=form.name.data)
        project.save()

    projects = models.Project.all().all()

    return render_template("projects.html", form=form, projects=projects)

@app.route(PROJECT_ROUTE + "<proj_id>")
def project_show(proj_id):
    """
    Show the files contained in a specific project.

    :param int proj_id: The ID of the desired project.
    """
    pass
