"""
Open, close, and manage database connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import mapped_classes

class Database:
    def __init__(self, url):
        """
        Create an engine object and create the tables (if they haven't already
        been created.
        """
        self.engine = create_engine(url)
        mapped_classes.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)