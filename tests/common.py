"""Common methods useful in all unit tests.
"""

from app import app
from app import db

def reset_db():
    """Clean the database and recreate the schema.
    """
    open(app.config["SQLALCHEMY_DATABASE_PATH"], "w").close()
    db.create_all()

