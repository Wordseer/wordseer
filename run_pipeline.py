from app.models.project import Project
import lib.wordseerbackend.wordseerbackend.collectionprocessor as colproc
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
colproc.cp_run(collection_dir, structure_file, extension, project)

