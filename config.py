# coding=utf-8
"""
==========================
Application Configurations
==========================

This module uses classes to set configurations for different environments.
"""

import os
import tempfile

#TODO: Change this for your use case
DEFAULT_ENV = "Development"

class BaseConfig(object):
    """This module contains application-wide configurations. It provides
    variables that are used in other configurations.
    """

    PROPAGATE_EXCEPTIONS = True

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

    SECRET_KEY = "secret"

    #Email settings
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
    SECURITY_SEND_REGISTER_EMAIL = False

    RELATIONS = {("none",): "search",
    ("",): "(any relation)",
    ("amod", "advmod",): "described as",
    ("agent", "subj", "nsubj", "csubj", "nsubjpass", "csubjpass",): "done by",
    ("obj", "dobj", "iobj", "pobj",): "done to",
    ("prep_because", "prep_because_of", "prep_on_account_of", "prep_owing_to"
        "prepc_because", "prepc_because_of", "prepc_on_account_of",
        "prepc_owing_to",): "because",
    ("conj_and",): "and",
    ("purpcl",): "in order to",
    ("prep_with", "prepc_with", "prep_by_means_of",
        "prepc_by_means_of",): "with",
    ("prep_to",): "to",
    ("prep_from",): "from",
    ("prep_of",): "of",
    ("prep_to",): "to",
    ("prop_from",): "from",
    ("prep_of",): "of",
    ("prep_on",): "on",
    ("prep_by",): "by",
    ("prep_in",): "in",
    ("poss",): "possessed by",
    }

    #TODO: unify these options with the pipeline

    STOPWORDS = (u"'ve ’s ’ 're does o t went was is had be were did are have "
        "do has being am 's been go 'm the and so are for be but this what 's "
        "did had they doth a to is that was as are at an of with . , ; ? ' \" "
        ": `").split();

    PUNCTUATION = list(u"!@#$%^&*()_+-=~`,./;;\"'{}[]|’\\");

    # Number of rows to return for paginated queries
    PAGE_SIZE = 100

class Production(BaseConfig):
    """Config for the production server.
    """

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.ROOT,
        BaseConfig.APP_NAME + ".db")

    SECRET_KEY = "secret" #TODO: change this in production

    # Emailing settings
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
    SECURITY_SEND_REGISTER_EMAIL = True

    #Email server settings
    #TODO: change in production
    MAIL_SERVER = "localhost"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = None
    MAIL_MAX_EMAILS = None

class Development(BaseConfig):
    """ This class has settings specific for the development environment.
    """
    DEBUG = True

    # CSRF settings for forms
    WTF_CSRF_ENABLED = True

    # Set database configurations
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.ROOT,
        BaseConfig.APP_NAME + "_dev.db")
    SQLALCHEMY_ECHO = True

class Testing(BaseConfig):
    """ This class has settings specific for the testing environment.
    """
    DEBUG = True

    # CSRF settings for forms
    WTF_CSRF_ENABLED = False

    # Set database configurations
    SQLALCHEMY_DATABASE_PATH = tempfile.mkstemp()[1]
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_PATH
    SQLALCHEMY_ECHO = False

    PAGE_SIZE = 10
