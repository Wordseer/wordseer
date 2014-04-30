# Modified from:
# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
import os
from sys import argv

os.environ['FLASK_ENV'] = "development"

from app import app, db

from migrate.versioning import api
import imp
import shutil
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URI = app.config["SQLALCHEMY_DATABASE_URI"]
SQLALCHEMY_MIGRATE_REPO = app.config["SQLALCHEMY_MIGRATE_REPO"]

def create():
    create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO,
            api.version(SQLALCHEMY_MIGRATE_REPO))

def migrate():
    migration = (SQLALCHEMY_MIGRATE_REPO +
        '/versions/%03d_migration.py' % (api.db_version(SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_MIGRATE_REPO) + 1))
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_MIGRATE_REPO)
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('New migration saved as ' + migration)
    print('Current database version: ' +
        str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def upgrade():
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' +
        str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def downgrade():
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    print('Current database version: ' +
        str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def drop():
    os.remove(SQLALCHEMY_DATABASE_URI.split('///')[-1])
    shutil.rmtree(SQLALCHEMY_MIGRATE_REPO)

def reset():
    # Remove old database if it's there
    try:
        os.remove(SQLALCHEMY_DATABASE_URI.split('///')[-1])
    except OSError:
        pass

    db.create_all()

def prep_test():
    try:
        if os.environ['FLASK_ENV'].lower() == 'testing':
            try:
                # Remove old database if it's there
                os.remove(SQLALCHEMY_DATABASE_URI.split('///')[-1])
            except OSError:
                pass

            db.create_all()
        else:
            print("Your envinronment configurations are not set to testing.")
    except KeyError:
        print("Your Flask environment is not set.")

if __name__ == "__main__":

    if argv[1] == "create":
        create()
    elif argv[1] == "migrate":
        migrate()
    elif argv[1] == "upgrade":
        upgrade()
    elif argv[1] == "downgrade":
        downgrade()
    elif argv[1] == "drop":
        drop()
    elif argv[1] == "reset":
        reset()
    elif argv[1] == "prep_test":
        prep_test()
    else:
        print(str(argv[1]) + " is not a valid database operation.")
