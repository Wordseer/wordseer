from app.models.project import Project
from app.preprocessor.collectionprocessor import cp_run
#from lib.wordseerbackend.wordseerbackend.database.readerwriter import ReaderWriter

import os
import database
import pdb

collection_dir = os.path.join("tests", "data", "articles")
extension = ".xml"
structure_file = os.path.join(collection_dir, "structure.json")

database.reset()

# pdb.set_trace()

project = Project()
project.save()
cp_run(collection_dir, structure_file, extension, project)

