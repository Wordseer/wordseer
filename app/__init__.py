import os
import logging.config
import json

from flask import Flask
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_wtf.csrf import CsrfProtect

from config import DEFAULT_ENV

import logging.config
import json

app = Flask(__name__)
csrf = CsrfProtect(app)

# Load configurations for current environment by reading in the environment
# variable FLASK_ENV and changing it to camel case with the title() function.
try:
    environment = os.environ['FLASK_ENV'].title()
    app.config.from_object('.'.join(["config", environment]))
except KeyError:
    app.config.from_object(".".join(["config", DEFAULT_ENV]))


try:
    # Load the JSON preferences
    preferences_path = os.path.join(app.config["ROOT"], "preferences.json")
    with open(preferences_path) as preferences_file:
        preferences = json.load(preferences_file)
except (ValueError, IOError):
    preferences = {"INSTALL_TYPE": "full"}

for key, value in preferences.items():
    app.config[key] = value

"""
===============
Database Set Up
===============
"""

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy(app)
from app.models import *

# make sure foreign keys are enabled for sqlite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

"""
Authentication setup
"""

user_datastore = SQLAlchemyUserDatastore(db, user.User,
    user.Role)
security = Security(app, user_datastore)

from app.uploader import uploader as uploader_bp
from app.wordseer import wordseer as wordseer_bp

app.register_blueprint(uploader_bp)
app.register_blueprint(wordseer_bp)

"""
==============
Logging Set Up
==============
"""

logfile = os.path.join(app.config["ROOT"], "logging.json")
logging.config.dictConfig(json.load(open(logfile)))

