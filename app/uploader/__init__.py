from flask import Blueprint

uploader = Blueprint('uploader', __name__, template_folder='templates')

from . import views
from . import models

uploader.jinja_env.globals['form_token'] = views.generate_form_token
