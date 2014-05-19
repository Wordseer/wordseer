from flask import Blueprint

uploader = Blueprint('uploader', __name__, template_folder='templates')

from . import views
from . import models

uploader.app_template_global(views.generate_form_token)
