from lib.wordseerbackend.wordseerbackend.collectionprocessor import CollectionProcessor
from lib.wordseerbackend.reader_writer import ReaderWriter

import os

collection_dir = os.path.join("lib", "wordseerbackend", "tests", "data", "shakespeare_mini")
extension = ".xml"
structure_file = os.path.join(collection_dir, "structure.json")

reader_writer = ReaderWriter()
collection_processor = CollectionProcessor(reader_writer)

collection_processor.process(collection_dir, structure_file, extension, False)
