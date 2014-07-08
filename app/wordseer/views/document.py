import json

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
        self.collection = request.args.get("collection")
        self.phrases = request.args.get("phrases")
        self.metadata = request.args.get("metadata")
        
#        query the doc  
        self.doc = Document.query.get(self.doc_id)
#        does it exist?
        if not self.doc:
            abort(400)

        # does it belong to user?
#        TODO: frontend needs to send the user id
#        if not self.doc.belongs_to():
#            abort(400)

    def list_properties(self, unit):
        """list all the Properties associated with the Unit"""
        properties = []
        
        for current_prop in unit.properties: 
            meta = PropertyMetadata.query.filter_by(
                display_name=current_prop.name).one()
            property = {
                "document_id": self.doc_id,
                "unit_name": unit.type,
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
        
        return properties
        
    def dispatch_request(self):
        """Functions for fetching a single document's sub-structure, along
        with the metadata associated with all sub-structures.

        Retrieves information about the document with the given ID. If
        $include_text is true, also includes the text of the document,
        otherwise only retrieves the metadata. The fields returned are
        those expected by {@link WordSeer.model.DocumentModel}"""

        units = {}
        children = {}
        properties = []
        
        if not self.include_text:
            properties = self.list_properties(self.doc)
            
        else:
            # TODO: assemble the full text that matches the given filters
            
            # query params
            if self.phrases:
                self.phrases = json.loads(self.phrases)
            if self.metadata: 
                self.metadata =json.loads(self.metadata)
            
            # TODO: requires some methods from GetMetadata class
            
            # retrieve all children of document unit
            units["document"] = {
                self.doc_id: {
                    "metadata": {},
                    "unit_id": self.doc_id, 
                    "unit_name": "document",
                    }
            }
            
            parent_ids = []
            unit_ids = []
            
            for unit in self.doc.children: 
                # TODO: recursively? but not nested
                # TODO: model method to retrieve entire subtree?
            
                unit_ids.append(unit.id)
                
                # create unit type key if not present
                if unit.name not in units: 
                    units[unit.name] = {}
                    parent_ids[unit.name] = {}
                    
                # create unit id key if not present
                if unit.id not in units[unit.name]:
                    units[unit.name][unit.id] = {
                        # the whole row from old document_structure table
                        # TODO: this seems redundant
                        "unit_id": unit.id,
                        "unit_name": unit.type,
                        "parent_id": unit.parent_id,
                        "parent_name": unit.parent.type,
                        "document_id": self.doc_id,
                        "unit_number": unit.number,
                        "metadata": self.list_properties(unit)
                    }
                    
                    parent_ids[unit.name][unit.id] = [
                        unit.parent_id,
                        unit.parent.type
                    ]
                    
                    if unit.name == "sentence":
                        units[unit.name][unit.id]["sentence_id"] = unit.id
                        
                        # Get the words in each sentence in the document.
                        units[unit.name][unit.id]["words"] = [
                            {
                                "word": word.word,
                                "word_id": word.id,
                                "space_after": "", # TODO: from WordInSentence
                                # TODO: phrase set memberships
                            } for word in unit.words
                        ]
                        
                    else:
                        if unit.type not in children:
                            children[unit.type] = {}
                        if unit.id not in children[unit.type]:
                            children[unit.type][unit.id] = {}    
        
            # The top-level metadata for the document is under the "document" unit,
            # so pull it out.    
            properties = units["document"][self.doc_id]["metadata"]

            
            

        results =  {
                "has_text": self.include_text,
                "units": units,
                "children": children,
                "id": self.doc_id,
                "metadata": properties,
                }
        
        # TODO: includes all metadata values again as dict keys: why? 
        for prop in properties: 
            results[prop["property_name"]] = prop["value"]
        
        return jsonify(results)
        
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