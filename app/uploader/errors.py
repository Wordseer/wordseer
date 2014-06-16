"""Error handlers for the wordseer blueprint.
"""

from . import exceptiomns
from . import uploader
from . import helpers

@uploader.errorhandler(exceptions.ProjectNotFoundException)
def project_not_found(error):
    """This handles the user trying to view a project that does not exist.
    """
    return helpers.not_found("project")

@uploader.errorhandler(exceptions.DocumentNotFoundException)
def document_not_found(error):
    """This handles the user trying to view a document that does not exist.
    """
    return helpers.not_found("document")

@uploader.errorhandler(404)
def page_not_found(error):
    """This handles the user trying to view a general page that does not exist.
    """
    return helpers.not_found("page")
