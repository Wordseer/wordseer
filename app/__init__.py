import os
from flask import Flask
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
CsrfProtect(app)

# Load configurations for current environment by reading in the environment
# variable FLASK_ENV and changing it to camel case with the title() function.
try:
    environment = os.environ['FLASK_ENV'].title()
    app.config.from_object('.'.join(["config", environment]))
except KeyError:
    print("Your Flask environment is not set.")
    exit(0)

"""
===============
Database Set Up
===============
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up database sessions for different environments
database = sessionmaker(
    bind=create_engine(app.config["SQLALCHEMY_DATABASE_URI"]))()

from app.views import *
from app.models import *
#app.jinja_env.globals['form_token'] = generate_form_token
