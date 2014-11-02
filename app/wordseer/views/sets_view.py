import datetime

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import MethodView
from sqlalchemy import func

from app import db
from app.models.flask_security import User
from app.models import *
from app.wordseer import wordseer

from app.helpers.application_view import register_rest_view


class SetsView(MethodView):
    """CRUD ``Set``s"""


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
            - sentence count
            - document count
        """
        if not set_id:
            if self.set_id:
                set_id = self.set_id
            else:
                abort(400)
        requested_set = Set.query.get(set_id)
        if not requested_set:
            abort(400)

        contents = {}
        contents["text"] = requested_set.name
        contents["id"] = requested_set.id
        contents["date"] = str(requested_set.creation_date)
        contents["type"] = requested_set.type
        if requested_set.type == "phrase":
            contents["phrases"] = [sequence.sequence for sequence in
                requested_set.sequences]
        else:
            contents["ids"] = [item.id for item in requested_set.get_items()]

        count = db.session.query(
            func.count(PropertyOfSentence.sentence_id.distinct()).label("sentence_count"),
            func.count(Sentence.document_id.distinct()).label("document_count")).\
            filter(Sentence.id == PropertyOfSentence.sentence_id).\
            filter(Property.name == requested_set.type + "_set").\
            filter(Property.value == requested_set.id).\
            filter(PropertyOfSentence.property_id == Property.id).first()
        contents["sentence_count"] = count.sentence_count
        contents["document_count"] = count.document_count

        return contents

    def sent_and_doc_counts(self):
        """count sentences and documents associated with the units in each ``Set``"""
        # TODO: php got both document and sentence counts from metadata table;
        # can we do that here?
        pass

    def list(self, parent_id=0):
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

        if self.collection_type:
            # retrieve Set records from this level
            setlist = []
            print parent_id
        
            sets = Set.query.filter_by(parent_id=parent_id, project=self.project,
                type=self.collection_type).all()
            
            for s in sets:
                print s
                setinfo = self.read(s.id)
        
                # TODO: get sentence and document counts
        
                # recurse through any nested Sets
                setinfo["children"] = self.list(s.id)
                setlist.append(setinfo)
        
            if parent_id == 0:
                # wrap setlist in the special root-level row
                all_sets = {
                    "text": '',
                    "id": 0,
                    "children": setlist,
                    "root": True,
                    "results": ''
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
        if self.collection_type:
            sets = Set.query.filter_by(project=self.project,
                type=self.collection_type).all()

            result = [self.read(s.id) for s in sets]

            # prepend special "all" set for document sets
            # TODO: frontend may send type as "document", need to change
            if self.collection_type == "document":
                alldocs = {
                    "text": "all",
                    "date": "",
                    "id": 0
                }
                result.insert(0, alldocs)

            return result
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
        if self.set_name and self.parent_id and self.collection_type:
            new_set = None
            set_type = None
            if self.collection_type == "phrase":
                set_type = SequenceSet
            elif self.collection_type == "sentence":
                set_type = SentenceSet
            elif self.collection_type == "document":
                set_type = DocumentSet
            new_set = set_type(
                    name=self.set_name,
                    creation_date=datetime.date.today(),
                    parent_id=self.parent_id,
                    type=self.collection_type,
                    project=self.project)
            new_set.save()

            #TODO: updateMainMetadataCounts?
            metadata = PropertyMetadata.query.filter_by(
                property_name = self.collection_type + "_set").first()
            if metadata is None:
                unit_type = self.collection_type
                if self.collection_type == "phrase":
                    unit_type = "sentence"

                metadata = PropertyMetadata(
                    property_name = self.collection_type + "_set",
                    data_type = "string",
                    is_category = True,
                    display_name = self.collection_type.capitalize() +" Set",
                    unit_type = unit_type)
                metadata.save()

            return {
                    "status": "ok", #TODO: let's get rid of this, 200 code is ok
                    "id": new_set.id,
                    "date": str(new_set.creation_date)
                }
        else:
            abort(400)

    def delete_set(self):
        """Delete the specified ``Set``

        Requires:
            -set_id

        Returns:
            status: ok
        """
        # php equivalent: subsets/create.php:delete()

        # required variables
        if self.set_id:

            # get the set or abort if it doesn't exist
            target_set = Set.query.get(self.set_id)
            if not target_set:
                abort(400)

            target_set.delete_metadata()

            # delete the set
            db.session.delete(target_set)
            db.session.commit()

            return {"status": "ok"}

        else:
            abort(400)

    def update_add_to_set(self):
        """Adds the given id's to the set with the given ID.

        Requires:
            - set_id: the ID of the ``Set`` to add the new item to
            - new_item: a ___-delimited string of various item attributes
        Returns:
        """

        if self.set_id and self.new_item:
            # do something
            target_set = Set.query.get(self.set_id)
            items = self.new_item.strip().split("___")
            # set = None
            # if target_set.type == "phrase":
            #     set = SequenceSet.query.get(self.set_id)
            # elif target_set.type == "sentence":
            #     set = SentenceSet.query.get(self.set_id)
            # elif target_set.tye == "document":
            #     set = DocumentSet.query.get(self.set_id)
            target_set.add_items(items)
            return {"status": "ok"}
        else:
            abort(400)

    def update(self):
        """Methods for adding, modifying, and deleting items within ``Set``\s;
        Has its own dispatch dict for various update types
        """
        if self.update_type:
            update_types = {
                "add": self.update_add_to_set,
                "delete": None,
                "rename": None,
                "move": None,
                "merge": None
            }

            # TODO: return utypes and dispatch the methods, when they exist
            return update_types[self.update_type]()

        else:
            abort(400)

    # possible type values to dispatch
    operations = {
        "read": read,
        "list": list,
        "listflat": list_flat,
        "create": create,
        "delete": delete_set,
        "update": update,
    }

    def get(self, **kwargs):
        """choose function from dispatch table with key == ``request.type``
        and jsonify it
        """
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
            self.operation = request.args["operation"]
            self.project = Project.query.get(kwargs["project_id"])
        except ValueError as e:
            print "\n\n\n\n", e, '\n\n\n\n'
            abort(400)
        # optional args depending on the operation requested
        self.set_id = request.args.get("id", type=int)
        self.collection_type = request.args.get("collectiontype")
        self.user_id = request.args.get("user", type=int)
        self.set_name = request.args.get("name")
        self.parent_id = request.args.get("parent")
        self.update_type = request.args.get("update")
        self.new_item = request.args.get("item")
        self.annotation = request.args.get("annotation")
        self.annotation_id = request.args.get("annotation", type=int)
        self.itemtype = request.args.get("itemType")
        self.note_id = request.args.get("noteID", type=int)
        self.text = request.args.get("text")
        self.new_name = request.args.get("newName")
        self.new_parent = request.args.get("newParent")
        self.merge_into = request.args.get("mergeInto")

        result = self.operations[self.operation](self)
        if type(result) == dict:
            return jsonify(result)
        else:
            return jsonify(results = result)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass

register_rest_view(
    SetsView,
    wordseer,
    'sets_view',
    'set',
    parents=["project"],
)
