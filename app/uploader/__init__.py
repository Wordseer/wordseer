import os

from flask import Blueprint

uploader = Blueprint('uploader', __name__,
    template_folder='templates',
    static_folder="static",
    static_url_path=os.path.dirname(__file__))

from . import views
from . import models

uploader.app_template_global(views.generate_form_token)
