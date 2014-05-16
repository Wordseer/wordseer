"""Config for the WordSeer website.
"""
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
APP_NAME = os.path.basename(ROOT)
DEBUG = True
PROPAGATE_EXCEPTIONS = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(ROOT, APP_NAME + ".db")
