import os
from flask import Flask
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_wtf.csrf import CsrfProtect

from config import DEFAULT_ENV

app = Flask(__name__)
CsrfProtect(app)

# Load configurations for current environment by reading in the environment
# variable FLASK_ENV and changing it to camel case with the title() function.
try:
    environment = os.environ['FLASK_ENV'].title()
    app.config.from_object('.'.join(["config", environment]))
except KeyError:
    app.config.from_object(".".join(["config", DEFAULT_ENV]))

"""
===============
Database Set Up
===============
"""

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

"""
Authentication setup
"""

from app.models import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from app.views import *

app.jinja_env.globals['form_token'] = generate_form_token
