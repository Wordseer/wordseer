"""Blueprint for the uploader.

The uploader handles creation and deletion of files and projects, as well as
sending them to the processing pipeline.
"""

import os

from flask import Blueprint

uploader = Blueprint('uploader', __name__,
    template_folder='templates',
    static_folder="static",
    static_url_path=os.path.dirname(__file__))

from .views import *
from . import models
from . import errors

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

uploader.app_template_global(generate_form_token)
