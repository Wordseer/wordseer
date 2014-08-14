from app.models.project import Project
from app.models.documentfile import DocumentFile
from app.preprocessor.collectionprocessor import cp_run

import os
import sys
import database

collection_name = "articles"

if len(sys.argv) > 1 and sys.argv[1]:
    collection_name = sys.argv[1]

collection_dir = os.path.join("tests", "data", collection_name)
extension = ".xml"
structure_file = os.path.join(collection_dir, "structure.json")

database.reset()

project = Project()
project.save()

files = [f for f in os.listdir(collection_dir) if
        os.path.isfile(os.path.join(collection_dir, f))]

for file_name in files:
    if os.path.splitext(file_name)[1] == extension:
        document_file = DocumentFile(path = os.path.join(collection_dir,
            file_name))
        project.document_files.append(document_file)


cp_run(collection_dir, structure_file, extension, project)