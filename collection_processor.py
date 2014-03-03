import os
import config
import database

class CollectionProcessor:
    # Todo: Figure out config stuff
    def process(self):        
        # Set up database
        db = database.Database(config.db_url)
        print db

a = CollectionProcessor()
a.process()
        