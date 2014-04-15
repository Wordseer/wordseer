from flask import render_template, request

from app import app
from .. import models
from .. import forms

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route("/projects/", methods=["GET", "POST"])
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

    for project in projects:
        print project.name
    
    return render_template("projects.html", form=form, projects=projects)
