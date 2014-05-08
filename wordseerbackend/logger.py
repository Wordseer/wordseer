"""
Manage log writing and reading to the database. Many events are stored in a
database rather than a convential textfile for speedy queries later on in
the pipeline.
"""

from database import database
from models import Log
from sqlalchemy.orm.exc import NoResultFound

REPLACE = "replace"
UPDATE = "update"

def log(item, value, replace_value):
    """Add a new log entry to the log table.

    :param str item: The item to log (think of it as a title).
    :param str value: The value of the logged item.
    :param str replace_value: if set to logger.REPLACE, this entry will replace
        the previous entry with the same value. If set to logger.UPDATE, then
        this entry will add on to the previous entry's value with this entry's
        value in the form "old [new]".
    :return None: None.
    """

    entry = Log(log_item=item, item_value=value)
    session = database.Database().session

    if REPLACE == replace_value:
        entry = session.merge(entry)

    elif UPDATE == replace_value:
        try:
            existing_entry = session.query(Log).\
                filter(Log.log_item == item).one()
        except NoResultFound:
            existing_entry = Log(log_item=item, item_value="")

        entry.item_value = existing_entry.item_value + " [" +\
            entry.item_value + "] "
        session.merge(entry)

    session.commit()
    session.close()

def get(item):
    """Get the value for a specific log item.

    :param string item: The item to retrieve.
    :return string: The value of the given item, blank if the item does
        not exist, the first one if there are several instances.
    """

    session = database.Database().session
    results = session.query(Log).filter(Log.log_item == item).first()

    if results:
        return results.item_value

    return ""
