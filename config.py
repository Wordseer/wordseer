import os
basedir = os.path.abspath(os.path.dirname(__file__))
app_name = os.path.basename(basedir) # assuming application name is same as folder

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, app_name + ".db")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db')
