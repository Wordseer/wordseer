from app import app
from .. import models

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route("/projects")
def projects_list():
    pass

@app.route("/projects/new")
def projects_new():
    pass
