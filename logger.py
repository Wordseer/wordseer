"""
Handle logging functions, using the Log mapped class.
"""

from mapped_classes import Log
import database

class Logger():
    def log(item, value, replace_value):
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
        entry = Log(log_item = item, item_value = value)
        

        #if "replace" in replace_value:
        #    entry = session.merge(entry)

        elif "update" in replace_value:
            try:
                existing_entry = session.query(Log).\
                    filter(Log.value == value).one()
            except MultipleResultsFound, e:
                print e
            except NoResultFound, e:
                existing_entry = Log(log_item = item, item_value = "")

            entry.value = existing_entry.value + " [" + entry.value + "] "

        with database.Database() as session:
            entry = session.merge(entry)
            session.commit()
            session.close()

    def get(item):
        session = database.Database()
        results = session.query(Log).filter(log.item == item)

        if len(results) > 0:
            return results[0].item_value

        return ""