import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app.models.document import Document
from app.models.property import Property
from app.models.property_metadata import PropertyMetadata
from app.models.sequence import Sequence
from app.wordseer import wordseer, views

from flask import request


class DocumentView(View):

    """Functions for fetching a single document's sub-structure, along
    with the metadata associated with all sub-structures.

    Retrieves information about the document with the given ID. If
    $include_text is true, also includes the text of the document,
    otherwise only retrieves the metadata. The fields returned are
    those expected by {@link WordSeer.model.DocumentModel}"""

    # php equiv: documents/get-document.php

    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation
        # required
        try:
            self.project_name = request.args["instance"]
            self.doc_id = request.args["id"]

        except ValueError:
            abort(400)

#        query the doc
        self.doc = Document.query.get(self.doc_id)
#        does it exist?
        if not self.doc:
            abort(400)

        # does it belong to user?
#        TODO: frontend needs to send the user id
#        if not self.doc.belongs_to():
#            abort(400)

#         deal with the rest of the variables
        self.include_text = request.args.get("include_text", type=bool)
        self.set = request.args.get("collection")
        self.sequences = request.args.get("phrases") # string: "('word' or 'phrase')_(id)"
        self.metadata = request.args.get("metadata")
        self.unit = request.args.get("unit")
        self.search = request.args.get("search")

    #===========================================================================
    # helper methods
    #===========================================================================
    
    def list_properties(self, unit):
        """list all the Properties associated with the Unit"""
        properties = []

        for current_prop in unit.properties:
            meta = PropertyMetadata.query.filter_by(
                display_name=current_prop.name).one()
            prop = {
                "document_id": self.doc_id,
                "unit_name": unit.type,
                "property_name": current_prop.name,
                "value": current_prop.value,
                "has_value": bool(current_prop.value),
                # TODO: doublecheck this is what it wants
                "property_id": meta.id,
                "format": "",
                "type": meta.type,
                "is_category": meta.is_category,
                "name_is_displayed": meta.display,
                "name_to_display": meta.display_name,
                # TODO: missing value_is_displayed in model
                "value_is_displayed": True,
            }
            properties.append(prop)

        return properties

    def list_unit_subtree(self, unit):
        """recursively get all the descendants of a unit, return flat list"""
        results = []
        for child in unit.children:
            results.append(child)
            nextlevel = self.list_unit_subtree(child)
            for grandchild in nextlevel:
                results.append(grandchild)
        return results
    
    def filter_sentences(self):
        """Returns the sentence id's that match the given filters.
        Also returns the document counts 
        Also consults the GET param "document_id" 
        """
        # TODO: run filters to get a list of sentence ids
        
        results = None
        
        # filter by metadata
        if self.metadata:
            properties = json.loads(self.metadata)
            # example format: 
            # {
            #    "string_sentence_set": ["{looking for}__14"],
            #    "string_Seeker Gender": ["Woman__Woman"]
            # }
            # keys: "(format)_(name)"

            # values: if format == string: ["(value)__(set id if set)", ...]
            #         else: ["(range0)__(range1)", ..]
            
            # parse the passed values
            for k, v in properties: 
                k = k.split("_")
                prop_type = k[0]
                prop_name = k[1:]
                # put prop name back together if it had an underscore in it
                prop_name = "_".join(prop_name)
                
                v = v.split("__")
                if prop_type == "string":
                    if "_set" in prop_name:
                        prop_value = v[1]
                    else:
                        prop_value = v[0]
                    
                    props_filtered = Property.query.filter_by(
                        name=prop_name, value=prop_value)
                else:
                    props_filtered = Property.query.filter(
                        Property.name == prop_name,
                        Property.value >= v[0],
                        Property.value <= v[1] 
                    )
                
                
                ids = [prop.id for prop in props_filtered]
                    
            
            
        elif self.doc_id:
            # just get that document?
            pass

        # short circuit
        if ids == []:
            return ids
        
        # filter by sets
        if self.set and self.set != "all":
            # TODO: don't have working retrieval methods for set views yet
            pass
        
        # filter by sequences
        if self.sequences:
            temp_ids = []
            for seq in self.sequences:
                if seq:
                    seq_id = views.sequences.SequenceView.get_sequence_ids(seq)
                    seq_obj = Sequence.query.get(seq_id)
                    for sentence in seq_obj.sentences:
                        temp_ids.add(sentence.document.id)
            
            if ids == None:
                ids =  temp_ids
            else:
                # intersect
                ids += temp_ids
        
        return ids
                    
        
        # return the intersected result
        
        #TODO: is an empty result set the same as "all"?
        # or return "all"
#         return "all"
    
    #===========================================================================
    # endpoint methods
    #===========================================================================

    def get_document(self):
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
            
            # TODO: requires some methods from GetMetadata class?

            # retrieve all children of document unit
            units["document"] = {
                self.doc_id: {
                    "metadata": self.list_properties(self.doc),
                    "unit_id": self.doc_id,
                    "unit_name": "document",
                }
            }

            parent_ids = {}
            unit_ids = []

            for unit in self.list_unit_subtree(self.doc):

                unit_ids.append(unit.id)

                # create unit type key if not present
                if unit.type not in units:
                    units[unit.type] = {}
                    parent_ids[unit.type] = {}

                # create unit id key if not present
                if unit.id not in units[unit.type]:
                    units[unit.type][unit.id] = {
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

                    parent_ids[unit.type][unit.id] = [
                        unit.parent_id,
                        unit.parent.type
                    ]

                    if unit.type not in children:
                        children[unit.type] = {}
                    if unit.id not in children[unit.type]:
                        children[unit.type][unit.id] = {}

                    if unit.parent.type not in children:
                        children[unit.parent.type] = {}

                    if unit.parent.id not in children[unit.parent.type]:
                        children[unit.parent.type][unit.parent.id] = []

                    children[unit.parent.type][unit.parent.id].append(
                        {"id": unit.id, "name": unit.type})
                    # TODO: also a unit above document with no name?

                # retrieve sentences separately bc they are not Units
                # TODO: will this cause any problems on the front end?
                units["sentence"] = {}
                for sentence in unit.sentences:
                    if sentence.id not in units["sentence"]:
                        units["sentence"][sentence.id] = {}

                    units["sentence"][sentence.id]["sentence_id"] = sentence.id

                    # Get the words in each sentence in the document.
                    units["sentence"][sentence.id]["words"] = [
                        {
                            "word": word.word,
                            "word_id": word.id,
                            "space_after": " ",  # TODO: from WordInSentence
                            # TODO: WordInSentence has space_before instead?
                            # TODO: phrase set memberships
                        } for word in sentence.words
                    ]

            # The top-level metadata for the document is under the "document" unit,
            # so pull it out.
            properties = units["document"][self.doc_id]["metadata"]

        results = {
            "has_text": self.include_text,
            "units": units,
            "children": children,
            "id": self.doc_id,
            "metadata": properties,
        }

        # TODO: includes all metadata values again as dict keys: why?
        for prop in properties:
            results[prop["property_name"]] = prop["value"]

        return results

    def get_property_fields(self, **kwargs):
        """Outputs a JSON-encoded list of metadata columns for the Document 
        Browser in the format: 
             [ { 'propertyName':metadata1Name,
                 'nameToDisplay':metadata1NameToDisplay,
                 'type':metadata1Type }, ... ]
        """

        print("\n\n\n\n\n")
        print(kwargs)
        print("\n\n\n\n\n")


        properties = []

        result = []
        for prop in properties:
            if prop["name_is_displayed"]:
                result.append({
                    "propertyName": prop["property_name"],
                    "nameToDisplay":  prop["name_to_display"],
                    "valueIsDisplayed": prop["value_is_displayed"],
                    "type": prop["type"]
                })
        return result

    def get_properties(self):
        """TODO: i have no idea what this endpoint is for; only seems to dispatch 
        functions from grammaticalsearch 
        """
        pass

    def get_search_results(self):
        """lists all the documents in a table
        """
#         do some filtering thing
        metadata = json.loads(self.metadata)
        search = json.loads(self.search)
        
        ids = self.filter_sentences()
         
        if ids == "all" and len(search) == 0:
            docs_query = Document.query.limit(25).order_by("id")
            docs = []
            for row in docs_query:
                doc = self.get_document(row.id)
                doc["matches"] = 0
                docs.append(doc)
        else: 
            # run a filtered query
            doc_ids = self.filter_sentences()
            docs_query = Document.query.get_all(doc_ids)
            docs = []
            for row in docs_query:
                doc = self.get_document(row.id)
                doc["matches"] = doc_ids.count(row.id)
                docs.append(doc)
            
        
#        TODO: update frontend, can't return top-level array
        return {"documents": docs}

    def dispatch_request(self):
        print("\n\n\n\n\n" + str(self) + "\n\n\n\n\n")
        operations = {
            "get_document": self.get_document,
            "get_property_fields": self.get_property_fields,
            "get_properties": self.get_properties,
            "get_search_results": self.get_search_results,
        }

        result = operations[self.operation](self)
        return jsonify(result)


# routing instructions
wordseer.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/api/documents/single/",
    view_func=DocumentView.as_view("doc_single", "get_document"))

wordseer.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/api/documents/get_property_fields/",
    view_func=DocumentView.as_view("get_property_fields", "get_property_fields"))

wordseer.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/api/documents/get_properties",
    view_func=DocumentView.as_view("doc_properties", "get_properties"))

wordseer.add_url_rule(app.config["PROJECT_ROUTE"] + "<int:project_id>" + "/api/documents/search_results", 
    view_func=DocumentView.as_view("doc_search_results", "get_search_results"))
