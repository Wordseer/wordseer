from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

"""
===============
Database Set Up
===============
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up database sessions for different environments
database = {}
database['dev'] = sessionmaker(bind=create_engine(app.config["SQLALCHEMY_DEV_DATABASE_URI"]))()
database['test'] = sessionmaker(bind=create_engine(app.config["SQLALCHEMY_TEST_DATABASE_URI"]))()


from app.controllers import *
from app.models import *
