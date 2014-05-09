"""
A skeleton models file just for this part of the pipeline.
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Log(Base):
    """
    A log entry, which is recorded in the database.
    """

    __tablename__ = "log"

    log_item = Column(String(100), nullable=False, primary_key=True)
    item_value = Column(Text, nullable=False)
