from app.preprocessor.collectionprocessor import CollectionProcessor
from app.preprocessor.database.readerwriter import ReaderWriter

import os
import database
import pdb

collection_dir = os.path.join("tests", "data", "much_ado")
extension = ".xml"
structure_file = os.path.join(collection_dir, "structure.json")

database.reset()

reader_writer = ReaderWriter()
collection_processor = CollectionProcessor(reader_writer)

# pdb.set_trace()
collection_processor.process(collection_dir, structure_file, extension, False)
