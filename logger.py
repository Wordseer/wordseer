"""
Handle logging functions, using the Log mapped class.
"""

import database
from models import Log
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

class Logger(object):
    """Manage log writing and reading to the database."""
    #TODO: maybe not make this a class?
    def log(self, item, value, replace_value):
        """
        Add a new log entry.

        Arguments:
        item -- the entry to log.
        value -- the name to log it under.
        replace_value -- if set to "replace", then this entry will replace
        the previous entry with the same value. If set to "update", then this
        entry will add on to the previous entry's value with this entry's
        value.
        """
        
        entry = Log(log_item=item, item_value=value)
        session = database.Database().session

        if "replace" in replace_value:
            entry = session.merge(entry)

        elif "update" in replace_value:
            try:
                existing_entry = session.query(Log).\
                    filter(Log.item_value == value).one()
            except MultipleResultsFound as e:
                pass
            except NoResultFound as e:
                existing_entry = Log(log_item=item, item_value="")

            entry.value = existing_entry.value + " [" + entry.value + "] "

        session.commit()
        session.close()

    def get(self, item):
        """Get the value for a specific log item.

        :param string item: The item to retrieve.
        :return string: The value of the given item, blank if the item does
        not exist, the first one if there are several instances.
        """
        session = database.Database().session
        results = session.query(Log).filter(Log.item_value == item)

        if len(results) > 0:
            return results[0].item_value

        return ""
