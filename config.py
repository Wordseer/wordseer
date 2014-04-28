"""
==========================
Application Configurations
==========================

This module uses classes to set configurations for different environments.
"""

import os

class BaseConfig(object):
    """ This module contains application-wide configurations. It provides variables
    that are used in other configurations.
    """

    # Set root folder and application name
    ROOT = os.path.abspath(os.path.dirname(__file__))
    APP_NAME = os.path.basename(ROOT) # assuming application name is same as folder

    # Migration settings for flask-migrate
    SQLALCHEMY_MIGRATE_REPO = os.path.join(ROOT, 'db')

class Development(BaseConfig):
    """ This class has settings specific for the development environment.
    """

    # Set database configurations
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.ROOT, BaseConfig.APP_NAME + "_dev.db")

class Testing(BaseConfig):
    """ This class has settings specific for the testing environment.
    """

    # Set database configurations
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.ROOT, BaseConfig.APP_NAME + "_test.db")
