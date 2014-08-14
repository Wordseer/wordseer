"""Models for logging functionality.
"""

from app import db
from .base import Base
from .mixins import NonPrimaryKeyEquivalenceMixin

class Log(db.Model, Base, NonPrimaryKeyEquivalenceMixin):
    """A log entry, which is recorded in the database.

    Attributes:
        log_item (string): The name of the log entry.
        item_value (string): The value of the logged entry.
    """

    id = db.Column(db.Integer, primary_key=True)
    log_item = db.Column(db.String(100), nullable=False, index=True)
    item_value = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))
    type = db.Column(db.String)

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "log"
    }

class ErrorLog(Log):
    """An error log.
    """

    __mapper_args__ = {
        "polymorphic_identity": "error"
    }

class WarningLog(Log):
    """A warning log.
    """

    __mapper_args__ = {
        "polymorphic_identity": "warning"
    }

class InfoLog(Log):
    """An info log.
    """

    __mapper_args__ = {
        "polymorphic_identity": "info"
    }

