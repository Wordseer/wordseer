from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class Document(View):
    """Various document-related functions"""
    
    def __init__(self):
        """deal with all the variables"""
        # required    
        try:
            self.project = request.args["instance"]
            self.doc_id = request.args["id"]
        except ValueError:
            abort(400)
            
        self.include_text = request.args.get("include_text", type=bool)
        
    def get_document(self):
        """Functions for fetching a single document's sub-structure, along
        with the metadata associated with all sub-structures.

        Retrieves information about the document with the given ID. If
        $include_text is true, also includes the text of the document,
        otherwise only retrieves the metadata. The fields returned are
        those expected by {@link WordSeer.model.DocumentModel}"""
        pass
    
    def get_document_search_results(self):
        """Called by view.js in service of view.php.
	Lists all the documents in a table
        """
        
        pass
    
    def get_metadata(self):
        """Gets... metadata?"""
        pass

    def get_metadata_fields(self):
        """Outputs a JSON-encoded list of metadata columns for the
        Document Browser in the format:
        [ { 'propertyName':metadata1Name,
         'nameToDisplay':metadata1NameToDisplay,
         'type':metadata1Type }, ... ]"""
        pass
