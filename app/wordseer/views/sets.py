import datetime

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import db
from app.models.flask_security import User
from app.models.sets import Set
from .. import wordseer

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
        self.parent_id = request.args.get("parent")
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

    def read(self, set_id=None):
        """Returns the contents of the ``Set`` with the given ID

        Requires:
            set_id (int): ID of the ``Set`` to list. falls back to query param
            as default

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
        if not set_id:
            if self.set_id:
                set_id = self.set_id
            else:
                abort(400)

        contents = {}
        requested_set = Set.query.get(set_id)

        contents["text"] = requested_set.name
        contents["id"] = requested_set.id
        contents["date"] = requested_set.creation_date
        contents["type"] = requested_set.type

        if requested_set.type == "sequenceset":
            contents["phrases"] = [sequence.sequence for sequence in
                requested_set.sequences]

        else:
            contents["ids"] = [item.id for item in requested_set.get_items()]

        return contents

    def sent_and_doc_counts(self):
        """count sentences and documents associated with the units in each ``Set``"""
        # TODO: php got both document and sentence counts from metadata table;
        # can we do that here?
        pass

    def list(self, parent_id=None):
        """Returns a recursive list of extant ``Set``\s of a given type

        Requires:
            collection_type (str): the type of ``Set`` desired
            user_id (int): ``User`` to whom the ``Set``\s belong

        Returns:
            - text: name of ``Set``
            - id: id of set (0 indicates root)
            - children: children of ``Set`` (recursive)
                - text
                - id
                - type
                - date
                - [ids or phrases]?
                - children
                - sentence_count
                - document_count
            - root: bool
        """
        # php equivalent: subsets/read.php:listCollections()
        # check for required args
        if self.collection_type and self.user_id:

            # retrieve Set records from this level
            setlist = []

            sets = Set.query.filter_by(parent_id=parent_id,
                user_id=self.user_id, type=self.collection_type).all()

            for set in sets:
                setinfo = self.read(set.id)

                # TODO: get sentence and document counts

                # recurse through any nested Sets
                setinfo["children"] = self.list(set.id)
                setlist.append(setinfo)

            if parent_id == None:
                # wrap setlist in the special root-level row
                all_sets = {
                    "text": '',
                    "id": 0,
                    "children": setlist,
                    "root": True
                    }
                return all_sets
            else:
                return setlist
        else:
            abort(400)

    def list_flat(self):
        """Performs ``read`` method on all ``Set``\s belonging to current
        ``User`` of given type; returns them in a non-recursive list.

        Requires:
            collection_type (str): the type of ``Set`` desired
            user_id (int): ``User`` to whom the ``Set``\s belong

        Returns:
            [{
            - date: Creation date of the ``Set``
            - text: Name of the ``Set``
            - type: Type of the ``Set``
            - id: ID of the ``Set``
            - phrases: If this is a ``SequenceSet``, a list
                of phrases in this ``Set``.
            - ids: If it's not a ``SequenceSet``, then a list of the item IDs in
                the ``Set``.
            }, {...}, ...]
        """
        # php equivalent: subsets/read.php:listCollectionsFlat()
        # check for required args
        if self.collection_type and self.user_id:

            sets = Set.query.filter_by(user_id=self.user_id,
                type=self.collection_type).order_by(Set.name).all()

            result = [self.read(set.id) for set in sets]

            # prepend special "all" set for document sets
            # TODO: frontend may send type as "document", need to change
            if self.collection_type == "documentset":
                alldocs = {
                    "text": "all",
                    "date": "",
                    "id": 0
                }
                result.insert(0, alldocs)

            # TODO: jsonify does not allow top-level lists for security reasons;
            # http://flask.pocoo.org/docs/security/#json-security
            # need to update the frontend accordingly
            return {"sets": result}
        else:
            abort(400)

    def create(self):
        """Create a new subset with the given information.

        Arguments:
            user_id (str): The ``User`` that should own this ``Set``
            set_name (str): The name of the ``Set`` to be created.
            parent_id (int): The id of the ``Set`` to nest it under
            collection_type (str): the type of ``Set``

        Returns:
            - "status": "ok" [TODO: eliminate this]
            - "id": int, ID of the newly created ``Set``
            - "date": str, date of creation of this ``Set``
        """
        # php equivalent: subsets/create.php:create()

        if self.user_id and self.set_name and self.parent_id \
            and self.collection_type:

            user = User.query.get(self.user_id)

            # TODO: set current creation date by default in model
            new_set = Set(name=self.set_name, parent_id=self.parent_id,
                type=self.collection_type, user=user)

            # TODO: should this be a model method?
            db.session.add(new_set)
            db.session.commit()

            #TODO: updateMainMetadataCounts? what does that even do?

            return {
                    "status": "ok", #TODO: let's get rid of this, 200 code is ok
                    "id": new_set.id,
                    "date": new_set.creation_date
                }
        else:
            abort(400)

    # possible type values to dispatch
    operations = {
        "read": read,
        "list": list,
        "listflat": list_flat,
        "create": create,
    }

    def dispatch_request(self):
        """choose function from dispatch table with key == ``request.type``
        and jsonify it
        """
        result = self.operations[self.operation](self)
        return jsonify(result)

# routing instructions
wordseer.add_url_rule('/api/sets/', view_func=CRUD.as_view("sets"))
