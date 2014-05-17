"""
Remove the existing database and create a new one.
"""

import os

from app import db
from app import config

def reset_db():
    # Remove old database if it's there
    try:
        os.remove(config.SQLALCHEMY_DATABASE_URI.split('///')[-1])
    except OSError:
        pass

    db.create_all()

if __name__ == "__main__":
   reset_db() 
