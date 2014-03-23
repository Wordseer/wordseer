from config import *
from models import Base, Log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DB_URL)
sessmaker = sessionmaker(engine)
session = sessmaker()

Base.metadata.create_all(engine)
session.add_all([
            Log(log_item="database_created", item_value="true"),
            Log(log_item="latest_parsed_sentence_number", item_value="0"),
            Log(log_item="latest_parsed_document_id", item_value="0")])
session.commit()
