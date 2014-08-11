from flask import render_template
from flask_security.decorators import login_required

from app import app
from .. import wordseer

@wordseer.route(app.config["PROJECT_ROUTE"]+"<int:project_id>"+
    app.config["ANALYZE_ROUTE"])
@login_required
def ext_app(project_id):
    return render_template('app.html', project_id=project_id)
