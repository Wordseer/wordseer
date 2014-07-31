"""Models for logging functionality.
"""

from app import db
from .base import Base

class Log(db.Model, Base):
    """A log entry, which is recorded in the database.

    Attributes:
        log_item (string): The name of the log entry.
        item_value (string): The value of the logged entry.
    """

    id = None # Log entries don't have IDs
    log_item = db.Column(db.String(100), nullable=False, primary_key=True)
    item_value = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

