"""
Manage log writing and reading to the database. Many events are stored in a
database rather than a convential textfile for speedy queries later on in
the pipeline.
"""
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.models.log import Log

REPLACE = "replace"
UPDATE = "update"

def log(project, item, value, replace_value):
    """Add a new log entry to the log table.

    :param str item: The item to log (think of it as a title).
    :param str value: The value of the logged item.
    :param str replace_value: if set to logger.REPLACE, this entry will replace
        the previous entry with the same value. If set to logger.UPDATE, then
        this entry will add on to the previous entry's value with this entry's
        value in the form "old [new]".
    :return None: None.
    """

    try:
        entry = Log.query.\
            filter(Log.log_item == item).\
            filter(Log.project == project).one()
    except NoResultFound:
        entry = Log(project=project, log_item=item, item_value="")

    if REPLACE == replace_value:
        entry.item_value = value
        entry.save()

    elif UPDATE == replace_value:
        entry.item_value = entry.item_value + " [" + value + "] "
        entry.save()

def get(project, item):
    """Get the value for a specific log item.

    :param string item: The item to retrieve.
    :return string: The value of the given item, blank if the item does
        not exist, the first one if there are several instances.
    """
    results = Log.query.filter(Log.log_item == item).\
            filter(Log.project == project).first()

    if results:
        return results.item_value

    return ""

