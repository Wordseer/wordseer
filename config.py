"""
==========================
Application Configurations
==========================

This module uses classes to set configurations for different environments.
"""

import os
import tempfile

DEFAULT_ENV = "Development"

class BaseConfig(object):
    """This module contains application-wide configurations. It provides
    variables that are used in other configurations.
    """

    # Set root folder and application name
    ROOT = os.path.abspath(os.path.dirname(__file__))
    # assuming application name is same as folder
    APP_NAME = os.path.basename(ROOT)

    # Migration settings for flask-migrate
    SQLALCHEMY_MIGRATE_REPO = os.path.join(ROOT, 'db')

    # Upload config
    UPLOAD_DIR = os.path.join(ROOT, 'app/uploads')
    ALLOWED_EXTENSIONS = ["xml", "json"]
    STRUCTURE_EXTENSION = "json"

    # Routing URLS
    PROJECT_ROUTE = "/projects/"
    DOCUMENT_ROUTE = "/documents/"
    UPLOAD_ROUTE = "/uploads/"

    #Login settings
    SECURITY_REGISTERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True
    

class Development(BaseConfig):
    """ This class has settings specific for the development environment.
    """

    # CSRF settings for forms
    WTF_CSRF_ENABLED = True
    SECRET_KEY = "secret" #TODO: change this in production

    # Set database configurations
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.ROOT,
        BaseConfig.APP_NAME + "_dev.db")
    SQLALCHEMY_ECHO = True

class Testing(BaseConfig):
    """ This class has settings specific for the testing environment.
    """

    # CSRF settings for forms
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "secret" #TODO: change this in production

    # Set database configurations
    SQLALCHEMY_DATABASE_PATH = tempfile.mkstemp()[1]
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_PATH
    SQLALCHEMY_ECHO = False
