from app.models.project import Project
from app.models.document import Document
from app.preprocessor.collectionprocessor import cp_run

import os
import database

collection_dir = os.path.join("tests", "data", "personals")
extension = ".xml"
structure_file = os.path.join(collection_dir, "structure.json")

database.reset()

project = Project()
project.save()

files = [f for f in os.listdir(collection_dir) if
        os.path.isfile(os.path.join(collection_dir, f))]

for file_name in files:
    if os.path.splitext(file_name)[1] == extension:
        document = Document(path = os.path.join(collection_dir, file_name))
        project.documents.append(document)


cp_run(collection_dir, structure_file, extension, project)

