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
    UPLOAD_DIR = os.path.join(ROOT, 'uploads')
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

    PREPOSITIONS = (u"about away across against along around at behind"
        " beside besides by despite down during for from in inside into"
        " near of off on onto over through to toward with within whence"
        " until without upon hither thither unto up").split(" ")

    PRONOUNS = (u"i its it you your thou thine thee we he they me us her"
        " them him my mine her hers his our thy thine ours their theirs"
        " myself itself mimself ourselves herself themselves anything"
        " something everything nothing anyone someone everyone ones"
        " such").split(" ")

    DETERMINERS = (u"the a an some any this these each that no every all"
        " half both twice one two first second other another next last"
        " many few much little more less most least several no"
        " own").split(" ")

    CONJUNCTIONS = (u"and or but so when as while because although if"
        " though what who where whom when why whose which how than nor "
        " not").split(" ")

    MODAL_VERBS = (u"can can't don't won't shan't shouldn't ca canst might"
        " may would wouldst will willst should shall must could").split(" ")

    PRIMARY_VERBS = (u"is are am be been being went go do did does doth has have"
        " hath was were had").split(" ")

    ADVERBS = (u"again very here there today tomorrow now then always never"
        " sometimes usually often therefore however besides moreover though"
        " otherwise else instead anyway incidentally meanwhile").split(" ")

    PUNCTUATION_ALL = (u". ! @ # $ % ^ & * ( ) _ - -- --- + = ` ’ ~ � { } [ ] | \\"
        " : ; \" ' < > ? , . / ").split(" ")

    CONTRACTIONS = (u"'re 've 's ’s'nt 'm n't th 'll o s 't 'rt t").split(" ")

    STOPWORDS = (PRONOUNS + PREPOSITIONS + DETERMINERS +
        CONJUNCTIONS + MODAL_VERBS + PRIMARY_VERBS + ADVERBS +
        PUNCTUATION_ALL + CONTRACTIONS)

    PUNCTUATION_NO_SPACE_BEFORE = list(u".,!`\\?';):—")
    PUNCTUATION_NO_SPACE_AFTER = list(u"`'\"(—")

    # Number of rows to return for paginated queries
    PAGE_SIZE = 100

    # Pipeline options
    #WORDSEER_DIR = os.path.dirname(os.path.realpath(__file__))

    # NLP locations. Paths should be absolute.
    CORE_NLP_DIR = os.path.join(ROOT, "lib/wordseerbackend/stanford-corenlp/")

    # Processing options
    GRAMMATICAL_PROCESSING = True
    PART_OF_SPEECH_TAGGING = True
    WORD_TO_WORD_SIMILARITY = True
    SEQUENCE_INDEXING = True

    # Database options
    #DB_URL = "sqlite:///" + os.path.join(ROOT, 'wordseer.db')


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
    SQLALCHEMY_ECHO = False

class Testing(BaseConfig):
    """ This class has settings specific for the testing environment.
    """
    DEBUG = True

    # CSRF settings for forms
    WTF_CSRF_ENABLED = False

    # Set database configurations
    # SQLALCHEMY_DATABASE_PATH = tempfile.mkstemp()[1]
    SQLALCHEMY_DATABASE_PATH = os.path.join(BaseConfig.ROOT, BaseConfig.APP_NAME + "_test.db")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_PATH

    SQLALCHEMY_DATABASE_CACHE_PATH = tempfile.mkstemp()[1]

    SQLALCHEMY_ECHO = False

    PAGE_SIZE = 10

