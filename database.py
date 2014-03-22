"""
Open, close, and manage database connections.
"""

import config
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#import models

class Database(object):
    """
    Manage connections with the database. This class is probably not necessary.
    """
    
    def __init__(self):
        """
        Create an engine object and create the tables (if they haven't already
        been created).
        """
        engine = create_engine(config.DB_URL)
        session = sessionmaker(bind=self.engine)
        self.session = session()

        created = session.query(models.Log).\
            filter_by(log_item == "database_created")

        if len(created) == 0 or "false" in created[0].item_value:
            self.reset()

        return self.session()

    #def reset(self):
        #"""
        #Create the tables again.
        #"""
        #models.Base.metadata.create_all(self.engine)
        #self.session.add_all([
            #Log(log_item="database_created", item_value="true"),
            #Log(log_item="latest_parsed_sentence_number", item_value="0"),
            #Log(log_item="latest_parsed_document_id", item_value="0")])

    def __exit__(self):
        self.session.close()
