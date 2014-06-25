import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class CRUD(View):
    """CRUD Sets"""
    def __init__(self):
        """initialize variables needed for Set operations

        request params:
        instance (str): ?
        type (str): Required
        id (int): Required if type in ["read", "delete"]
            or if type in ["update"] and update in ["add", "delete", "rename",
            "move","merge"]
        collectiontype (str): Required if type in ["list", "listflat", "create"]
        user (str): Required if type in ["list", "listflat", "create"]
            or type in ["update"] and update in ["addNote", "addTag"]
        name (str): Required if type in ["create"]
        parent (?): Required if type in ["create"]
        update (str): Required if type in ["update"]
        item (int): Required if type in ["update"] and update in ["add",
            "delete", "addNote", "addTag", "deleteNote", "deleteTag"]
        annotation (?): Required if type in ["update"] and update in ["addNote",
            "addTag"]
        annotationID (int): Required if type in ["update"] and update in
            ["deleteNote", "deleteTag"]
        itemType (str): Required if type in ["update"] and update
            in ["addNote", "addTag"]
        noteID (int): Required if type in ["update"] and update in ["editNote"]
        text (str): Required if type in ["update"] and update in ["editNote"]
        newName (str): Required if type in ["update"] and update in ["rename"]
        newParent (?): Required if type in ["update"] and update in ["move"]
        mergeInto (?): Required if type in ["update"] and update in ["merge"]
        """
        # required args
        try:
            self.type = request.args["type"]
            self.instance = request.args["instance"]
        except ValueError:
            abort(400)
        # optional args depending on the operation requested
        self.id = request.args.get("id", None)
        self.collectiontype = request.args.get("collectiontype", None)
        self.user = request.args.get("user", None)
        self.name = request.args.get("name", None)
        self.parent = request.args.get("parent", None)
        self.update = request.args.get("update", None)
        self.item = request.args.get("item", None)
        self.annotation = request.args.get("annotation", None)
        self.annotation_id
        self.itemtype = request.args.get("itemType", None)
        self.note_id = request.args.get("noteID", None)
        self.text = request.args.get("text", None)
        self.new_name = request.args.get("newName", None)
        self.new_parent = request.args.get("newParent", None)
        self.merge_into = request.args.get("mergeInto", None)

    def read(self):
        """Returns the contents of the Set with the given ID"""
        # check for required args
        if self.id:
            # MODEL METHOD: retrieve a set by ID
            # php equivalent: subsets/read.php:listSubsetContents()
        else:
            abort(400)

    # possible type values to dispatch
    types = dict()
    types["read"] = read

    def dispatch_request(self):
        """create a JSON response to the request"""
        pass
