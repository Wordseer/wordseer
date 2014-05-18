from flask import request

from app import app
from app import db

def table_exists(table):
    """Check if the given table exists in the database.

    Args:
        table (str): A table to check for.

    Returns:
        boolean: True if it does, False otherwise.
    """
    existing_tables = db.metadata.tables.keys()

    try:
        existing_tables.index(table)
    except ValueError:
        return False
    return True

def get_name_from_relation(relation):
    """Given a relation, return a human-readable name. This method is configured
    using a dict in config.py.
    """
    for relations, name in app.config["RELATIONS"].iteritems():
        if relation in relations:
            return name
