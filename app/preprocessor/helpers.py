"""General helper methods for the preprocessor.
"""

from app.models.log import ErrorLog

def log_error(logger, project, message, force=True):
    """Log an error with the given logger and set it on the project as well.

    Arguments:
        logger (Logger): The logger to use.
        project (Project): The project to use.
        message (tuple): A tuple like so::

            ("foo %s", "bar")

        force (boolean): Commit immediately if ``True``.
    """

    logger.error(*message)

    try:
        project.logs.append(ErrorLog("Error", message[0] % message[1:]))
    except IndexError:
        project.logs.append(ErrorLog("error", message[0]))

    project.save(force)

