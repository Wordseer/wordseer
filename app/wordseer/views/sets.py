import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app.models.sets import Set

class CRUD(View):
    """CRUD ``Set``s"""
    def __init__(self):
        """initialize variables needed for ``Set`` operations

        request params:
        instance (str): Required
        type (str): Required
        id (int): Required if ``type`` in ["read", "delete"]
            or if ``type`` in ["update"] and ``update`` in ["add", "delete", "rename",
            "move","merge"]
        collectiontype (str): Required if ``type`` in ["list", "listflat", "create"]
        user (int): Required if ``type`` in ["list", "listflat", "create"]
            or ``type`` in ["update"] and ``update`` in ["addNote", "addTag"]
        name (str): Required if ``type`` in ["create"]
        parent (?): Required if ``type`` in ["create"]
        update (str): Required if ``type`` in ["update"]
        item (int): Required if ``type`` in ["update"] and ``update`` in ["add",
            "delete", "addNote", "addTag", "deleteNote", "deleteTag"]
        annotation (?): Required if ``type`` in ["update"] and ``update`` in ["addNote",
            "addTag"]
        annotationID (int): Required if ``type`` in ["update"] and ``update`` in
            ["deleteNote", "deleteTag"]
        itemType (str): Required if ``type`` in ["update"] and ``update``
            in ["addNote", "addTag"]
        noteID (int): Required if ``type`` in ["update"] and ``update`` in ["editNote"]
        text (str): Required if ``type`` in ["update"] and ``update`` in ["editNote"]
        newName (str): Required if ``type`` in ["update"] and ``update`` in ["rename"]
        newParent (?): Required if ``type`` in ["update"] and ``update`` in ["move"]
        mergeInto (?): Required if ``type`` in ["update"] and ``update`` in ["merge"]
        """
        # TODO: does frontend send username or user ID? we need the ID

        # required args
        try:
            self.operation = request.args["type"]
            self.instance = request.args["instance"]
        except ValueError:
            abort(400)
        # optional args depending on the operation requested
        self.set_id = request.args.get("id", type=int)
        self.collection_type = request.args.get("collectiontype")
        self.user_id = request.args.get("user", type=int)
        self.set_name = request.args.get("name")
        self.parent = request.args.get("parent")
        self.update_type = request.args.get("update")
        self.item_id = request.args.get("item", type=int)
        self.annotation = request.args.get("annotation")
        self.annotation_id = request.args.get("annotation", type=int)
        self.itemtype = request.args.get("itemType")
        self.note_id = request.args.get("noteID", type=int)
        self.text = request.args.get("text")
        self.new_name = request.args.get("newName")
        self.new_parent = request.args.get("newParent")
        self.merge_into = request.args.get("mergeInto")

    def read(self):
        """Returns the contents of the ``Set`` with the given ID

        Requires:
            set_id (int): ID of the ``Set`` to list.

        Returns:
            Contents of the requested ``Set``, a dict with the following
            fields:

            - date: Creation date of the ``Set``
            - text: Name of the ``Set``
            - type: Type of the ``Set``
            - id: ID of the ``Set``
            - phrases: If this is a ``SequenceSet``, a list
                of phrases in this ``Set``.
            - ids: If it's not a ``SequenceSet``, then a list of the item IDs in
                the ``Set``.
        """
        # php equivalent: subsets/read.php:listSubsetContents()
        #TODO: why don't we just return a list of IDs in both cases?
        #TODO: why do we need to return the ID?

        # check for required args
        if self.set_id:
            contents = {}
            requested_set = Set.query.get(set_id)

            contents["text"] = requested_set.name
            contents["id"] = requested_set.id
            contents["date"] = requested_set.date
            contents["type"] = requested_set.type

            if requested_set.type == "sequenceset":
                contents["phrases"] = [sequence.sequence for sequence in
                    requested_set.sequences]

            else:
                contents["ids"] = [item.id for item in requested_set.get_items()]

            return jsonify(contents)

        else:
            abort(400)



    # possible type values to dispatch
    operations = dict()
    operations["read"] = read

    def dispatch_request(self):
        """create a JSON response to the request"""
        pass
