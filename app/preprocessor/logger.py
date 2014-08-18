"""
Manage log writing and reading to the database. Many events are stored in a
database rather than a convential textfile for speedy queries later on in
the pipeline.
"""
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.models.log import Log, ErrorLog, WarningLog, InfoLog

REPLACE = "replace"
UPDATE = "update"

class ProjectLogger(object):
    """Perform logging information that uses python logging as well as writing
    to a project's log entries.
    """

    def __init__(self, logger, project):
        """Instantiate a ``ProjectLogger``.

        Arguments:
            logger (Logger): A python logger to use.
            project (Project): A Project to log to.
        """
        self.logger = logger
        self.project = project

    def log(self, message_type, message, log_class, *args, **kwargs):
        """Generic message logger.

        Arguments:
            message_type (callback): A callback to call with the message and
                args.
            messsage (str): The text of the message.
            args: Formatting replacements for the string, as used by python's
                ``logging`` module.

        Keyword Arguments:
            force (boolean): Commit immediately if ``True`` (default ``True``).
            log_item (string): What to use for the ``log_item`` field (default
                ``Log message``).
        """
        force = kwargs.get("force", True)
        log_item = kwargs.get("log_item", "Log message")

        message_type(message, *args)
        self.project.logs.append(log_class(log_item=log_item,
            item_value=message % args))

        self.project.save(force)

    def info(self, message, *args, **kwargs):
        """Log an info with the given logger and set it on the project as well.

        Arguments:
            logger (Logger): The logger to use.
            message (str): The text of the message.
            args: Formatting replacements for the string.

        Keyword Arguments:
            force (boolean): Commit immediately if ``True`` (default ``True``).
        """
        kwargs["log_item"] = kwargs.get("log_item", "Info")
        self.log(self.logger.info, message, InfoLog, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """Log a warning with the given logger and set it on the project as well.

        Arguments:
            logger (Logger): The logger to use.
            message (str): The text of the message.
            args: Formatting replacements for the string.

        Keyword Arguments:
            force (boolean): Commit immediately if ``True`` (default ``True``).
        """
        kwargs["log_item"] = kwargs.get("log_item", "Warning")
        self.log(self.logger.warning, message, WarningLog, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Log an error with the given logger and set it on the project as well.

        Arguments:
            logger (Logger): The logger to use.
            message (str): The text of the message.
            args: Formatting replacements for the string.

        Keyword Arguments:
            force (boolean): Commit immediately if ``True`` (default ``True``).
        """
        kwargs["log_item"] = kwargs.get("log_item", "Error")
        self.log(self.logger.error, message, ErrorLog, *args, **kwargs)

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

