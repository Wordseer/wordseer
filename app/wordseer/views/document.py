from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app.models.document import Document
from app.models.property_metadata import PropertyMetadata
from app.wordseer import wordseer

class GetDocument(View):
    """Functions for fetching a single document's sub-structure, along
    with the metadata associated with all sub-structures.

    Retrieves information about the document with the given ID. If
    $include_text is true, also includes the text of the document,
    otherwise only retrieves the metadata. The fields returned are
    those expected by {@link WordSeer.model.DocumentModel}"""
    # php equiv: documents/get-document.php

    
    def __init__(self):
        """deal with all the variables"""
        # required    
        try:
            self.project_name = request.args["instance"]
            self.doc_id = request.args["id"]
                
        except ValueError:
            abort(400)
        
        self.include_text = request.args.get("include_text", type=bool)
        
#        query the doc  
        self.doc = Document.query.get(self.doc_id)
#        does it exist?
        if not self.doc:
            abort(400)

        # does it belong to user?
#        TODO: frontend needs to send the user id
#        if not self.doc.belongs_to():
#            abort(400)

        
    def dispatch_request(self):
        """Functions for fetching a single document's sub-structure, along
        with the metadata associated with all sub-structures.

        Retrieves information about the document with the given ID. If
        $include_text is true, also includes the text of the document,
        otherwise only retrieves the metadata. The fields returned are
        those expected by {@link WordSeer.model.DocumentModel}"""

        units = []
        children = []
        properties = []
        
        if not self.include_text:
#            get all the Properties associated with the Document
            for current_prop in self.doc.properties: 
                meta = PropertyMetadata.query.filter_by(display_name=current_prop.name).one()
                property = {
                    "document_id": self.doc_id,
                    "unit_name": "document",
                    "name": current_prop.name,
                    "value": current_prop.value,
                    "has_value": bool(current_prop.value),
                    "property_id": meta.id, #TODO: doublecheck this is what it wants
                    "format": meta.type,
                    "is_category": meta.is_category,
                    "name_is_displayed": meta.display,
                    "name_to_display": meta.display_name,
                }
                properties.append(property)
        else:
            # assemble the full text
            pass
        

        return jsonify({
                "has_text": self.include_text,
                "units": units,
                "children": children,
                "id": self.doc_id,
                "metadata": properties,
                })        
        # TODO: old code includes all the metadata twice, is that necessary?
        
# routing instructions
wordseer.add_url_rule("/api/documents/single/", 
    view_func=GetDocument.as_view("doc_single"))


class GetDocumentSearchResults(View):
    """Called by view.js in service of view.php.
	Lists all the documents in a table"""
    pass

class GetMetadata(View):
    """Gets... metadata?"""
    pass

class GetMetadataFields(View):
    """Outputs a JSON-encoded list of metadata columns for the
    Document Browser in the format:
    [ { 'propertyName':metadata1Name,
     'nameToDisplay':metadata1NameToDisplay,
     'type':metadata1Type }, ... ]"""
    pass