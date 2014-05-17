from flask import request

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
