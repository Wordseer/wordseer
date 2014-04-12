import os
basedir = os.path.abspath(os.path.dirname(__file__))
# assuming application name is same as folder
app_name = os.path.basename(basedir) 

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, app_name + ".db")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db')

CSRF_ENABLED = True
SECRET_KEY = "secret" #TODO: change this in production
