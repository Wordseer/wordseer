from app.preprocessor.collectionprocessor import CollectionProcessor

import os
import database
import pdb

collection_dir = os.path.join("tests", "data", "personals")
extension = ".xml"
structure_file = os.path.join(collection_dir, "structure.json")

database.reset()

collection_processor = CollectionProcessor()

# pdb.set_trace()
collection_processor.process(collection_dir, structure_file, extension, False)
