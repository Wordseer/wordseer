"""
Classes mapped to the database using sqlalchemy.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

# Sample implementation of table from database.java
class Highlight(Base):
    __tablename__ = "highlight"

    id = Column(Integer, primary_key=True, nullable=False)
    document_id = Column(Integer, primary_key=True, nullable=False, default=0)
    start = Column(Integer, primary_key=True, nullable=False, default=0)
    end = Column(Integer, primary_key=True, nullable=False, default=0)
    start_index = Column(Float, primary_key=True, nullable=False, default=0)
    end_index = Column(Float, primary_key=True, nullable=False, default=0)
    user = Column(String(45), index=True, nullable=False, default="")
    startNumber = Column(Float, nullable=False, default=0)
    endNumber = Column(Float, nullable=False, default=0)

