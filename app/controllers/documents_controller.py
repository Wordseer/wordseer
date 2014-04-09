from app import app

"""
This is the controller for pages related to documents.
"""

"""
The index action, which shows all files for a user.

Eventually, this will be swapped out for the more useful page that shows all
files in a collection.
"""
@app.route('/documents/')
def document_index():
    pass

"""
The show action, which shows details for a particular document.
"""
@app.route('/document/<id>')
def document_show(id):
    pass

"""
The new action for documents, which shows a form for uploading
document files to process.
"""
@app.route('/document/new')
def document_new():
    pass

"""
The create action for documents, which takes in document files, processes them,
and creates the corresponding database records.

NOTE: you don't need to implement the processing and database stuff since
obviously I'm still working on that; just implement enough to confirm that the
file was properly uploaded and would be ready for processing.
"""

@app.route('/document/create/')
def document_create():
    pass
