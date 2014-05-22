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
from . import models

"""
Authentication setup
"""

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)

from app.uploader import uploader as uploader_bp
from app.wordseer import wordseer as wordseer_bp

app.register_blueprint(uploader_bp, static_folder="static/uploader")
app.register_blueprint(wordseer_bp)
