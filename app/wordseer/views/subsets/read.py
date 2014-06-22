"""Called by ``subsets.js`` in service of all of the main pages.
Returns the contents of subsets and lists all the subsets made by a user.
"""
from flask import jsonify

from app.models import Set

def list_subset_contents(set_id):
    """Return the contents of the ``Set`` with the given ID.

    Arguments:
        subset_id (int): ID of the ``Set`` to list.

    Returns:
        list: Contents of the requested ``Set``, a dict with the following
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
    #TODO: why don't we just return a list of IDs in both cases?
    #TODO: why do we need to return the ID?

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

def get_highlight_text(start, start_index, end, end_index):
    """???

    Arguments:
        start
        start_index
        end
        end_index
    """
    #TODO: this has nothing to do with highlights, whatever those are

    pass

