"""Blueprint for the uploader.

The uploader handles creation and deletion of files and projects, as well as
sending them to the processing pipeline.
"""

import os

from flask import Blueprint

uploader = Blueprint('uploader', __name__,
    template_folder='templates',
    static_folder="static",
    static_url_path="/" + os.path.dirname(__file__))

from .views import *

from . import errors

uploader.app_template_global(views.generate_form_token)
