import os
from lib.wordseerbackend.reader_writer import ReaderWriter
from lib.wordseerbackend.wordseerbackend.collectionprocessor import CollectionProcessor
from database import prep_test

prep_test()

doc_dir = os.path.join('lib', 'wordseerbackend', 'tests', 'data', 'articles')
doc_type = '.xml'
doc_struct = 'structure.json'

reader_writer = ReaderWriter()
collection_processor = CollectionProcessor(reader_writer)

collection_processor.process(doc_dir, os.path.join(doc_dir, doc_struct), doc_type, False)
