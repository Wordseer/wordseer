"""Called by ``subsets.js`` in service of all of the main pages.
Returns the contents of subsets and lists all the subsets made by a user.
"""
from flask import jsonify

from app.models import Set
from app.models.association_objects import WordInSentence

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
    """Return ``Words`` that meet the given criteria.

    The query uses three conditionals to pick which ``Words`` to select:

    1. If the ID of the ``Word``'s ``Sentence`` is greater than ``start`` and
        less than ``end``
    2. Or if the ID of the ``Word``'s ``Sentence`` is equal to ``start``
        and the position of the ``Word`` is at least ``start_index``
    3. Or if the ID of the ``Word``'s ``Sentence`` is equal to ``end`` and
        the position of the ``Word`` is at most ``end_index``.


    Arguments:
        start (int): The minimal sentence ID or the sentence ID.
        start_index (int): The position of the word must be at least this.
        end (int): The maximum sentence ID or the sentence ID.
        end_index (int): Maximum position of the word.

    Returns:
        string: All the ``surface`` attributes from the matched ``Words`` put
        together, separated by spaces; ``surface``s with punctuation in them
        will not have a space before them.
    """
    #TODO: this has nothing to do with highlights, whatever those are
    #TODO: this method is ridiculous, how is it usable? the arguments could
    # mean two different things.
    text = ""
    words = WordInSentence.query.filter(
        (WordInSentence.sentence_id > start) &
            (WordInSentence.sentence_id < end) |
        (WordInSentence.sentence_id == start) &
            (WordInSentence.position >= start_index) |
        (WordInSentence.sentence_id == end) &
            (WordInSentence.position <= end_index)).\
                order_by(WordInSentence.sentence_id).\
                order_by(WordInSentence.position).all()

    for word in words:
        if not app.config["PUNCTUATION_ALL"] in word.surface:
            text += " " # Don't put spaces in front of punctuation.

        text += word.surface

    return text

