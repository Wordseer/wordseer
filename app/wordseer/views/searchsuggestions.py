"""????
"""

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View
from sqlalchemy import _not
from sqlalchemy import func
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import literal_column

from .. import wordseer
from ..models import PropertyMetadata
from ..models import WorkingSet
from ...uploader.models import Property
from ...uploader.models import Sequence
from ...uploader.models import SequenceInSentence
from app import db

class AutoSuggest(View):
    """Retrieve a list of suggested ``Set``s, ``Sequence``s, and ``Property``s.
    """
    def __init__(self):
        """Get necessary query variables and set filters.

        The ``query`` will be queried using a ``LIKE`` clause with ``%`` on
        either side of the string; so the ``query`` could be anywhere
        in the suggestions.

        If ``user`` is not supplied, a 400 error will be raised.

        Keyword Arguments:
            user (str): The name of the user performing the query.
            query (str): (optional) The word that the user has entered into the
                search bar so far.

        """
        self.query = request.args.get("query")
        #TODO: can we use userid instead?
        self.user = request.args.get("user")

        self.workingset_name_filter = True
        self.property_value_filter = True

        if self.query:
            like_query = "%" + query + "%"
            self.workingset_name_filter = WorkingSet.name.like(like_query)
            self.property_value_filter = Property.value.like(like_query)


    def dispatch_request(self):
        """Return a JSON list of suggestions.

        The list has a maximum of three types of suggestions: ``Set``s,
        ``Property``s, and ``Sequence``s. The response is formed like so::

            {
                "results": [
                    { ...suggested Set...  }
                    { ...suggested Property... }
                    { ...suggested Sequence... }
                ]
            }

        The specific structure of the dicts that make up the list in "results"
        can be found in documentation for ``get_suggested_sets``,
        ``get_suggested_properties``, and ``get_suggested_sequences``. Each
        function returns a list, all the lists are joined together into one.

        Note that ``get_suggested_sequences`` is only run if the length of the
        ``query`` is >= 2.

        Returns:
            A JSON response, or a 400 error if ``user`` is not supplied.
        """

        if not self.user:
            abort(400)

        suggestions = get_suggested_sets()
        suggestions.extend(get_suggested_properties())

        if len(query) >= 2:
            suggestions.extend(get_suggested_sequences())

        return jsonify(results=suggestions)

    def get_suggested_sets(self):
        """Return a list of dicts of suggestions of ``Set``s that may
        match the query.

        The query queries both ``Sets`` and ``Property``s.

        ``Set``s are filtered on the following criteria:

        * Have the same ``user`` as the one given in the request
        * Contain the ``query`` from the url, if applicable

        ``Property``s are filtered by the following criteria:

        * ``unit_name`` is equal to ``sentence``
        * ``value`` is equal to the ``id`` of the ``Set``
        * ``name`` is ``phrase_set``

        Returns:
            list of dicts: A list containing dicts with the following info::

                [
                    {
                        "id": int, id of the Set
                        "text": string, name of the Property
                        "class": "phrase-set"
                        "unit_count": int, how many Units have this property
                    }
                    ...etc...
                ]
        """
        #TODO: Mystery clause
        #TODO: document_count
        sets = db.session.query(WorkingSet.id,
            Property.name.label("text"),
            literal_column("'phrase-set'").label("class")
            func.count(Property.unit_id.distinct()).label("unit_count")).\
                filter(Property.unit_name == "sentence").\
                filter(Property.value == WorkingSet.id).\
                filter(WorkingSet.username == user).\
                filter(Property.name == "phrase_set").\
                filter(self.workingset_name_filter).\
                group_by(WorkingSet.name).\
                all()

        return [set._asdict() for set in sets]

    def get_suggested_properties(self):
        """Return a list of dicts of suggestions of ``Property``s that
        match the query.

        The query queries both ``Property`` and ``PropertyMetadata``.

        ``Property``s are filtered by the following criteria:

        * ``value`` contains the user's ``query``, if any
        * ``Property.name`` is equal to ``PropertyMetadata.property_name``
        * The ``Property`` is a category (``is_category`` is true for these
            ``Property``s)
        * ``Property.name`` does not contain ``_set``.

        Returns:
            list of dicts: A list of dicts with the following info::

                [
                    {
                        "display_name": str, display_name for this Property
                        "name: str, name of this Property
                        "value": str, value of this Property
                        "class": "metadata",
                        "unit_count": int, number of Units containing this
                            metadata
                    }
                ]
        """
        suggested_metadata = []
        #TODO: document_count, sentence_count
        metadata = db.session.query(PropertyMetadata.display_name,
            Property.name,
            Property.value,
            literal_column("'metadata'").label("class"),
            func.count(Property.unit_id.distinct()).label("unit_count")).\
                filter(self.property_value_filter).\
                filter(Property.name == PropertyMetadata.property_name).\
                filter(PropertyMetadata.is_category == True).\
                filter(not_(Property.name.like("%_set"))).\
                group_by(Property.value).\
                limit(50).\
                all()

        for metadatum in metadata:
            property_name = metadata.name
            if metadatum.display_name:
                property_name = metadatum.display_name

            suggestion = metadatum._asdict()
            suggestion["text"] = {property_name.lower(): metadatum.value}
            suggested_metadata.append(suggestion)

        return suggested_metadata

    def get_suggested_sequences():
        """Return a list of dicts of suggestions of ``Sequence``s that
        match the query.

        ``Sequence``s are filtered by the following criteria:

        * ``Sequence.sequence`` starts with ``query``

        Returns:
            list of dicts: A list of dicts with the following info::

                [
                    {
                        id: int, ID of this Sequence
                        text: sequence of this Sequence
                        length: length of this Sequence
                        class: "sequence",
                        "sentence_count": number of sentences this Sequence
                            is a part of
                    }
                ]
        """
        #TODO: document_count
        suggested_sequences = []
        sequences = db.session.query(Sequence.id,
            Sequence.sequence.label("text"),
            Sequence.length,
            literal_column("'sequence'").label("class"),
            func.count(SequenceInSentence.sentence_id).\
                label("sentence_count")).\
                    join(SequenceInSentence).\
                    filter(Sequence.sequence.like(query + "%")).\
                    order_by("sentence_count").\
                    order_by(asc(Sequence.length)).\
                    limit(50).\
                    all()

        for sequence in sequences:
            text = sequence.text.lower()

            if text in sequence_list and text is not None:
                sequence_list[text] = 1
                suggested_sequences.append(sequence._asdict())

        return suggested_sequences

wordseer.add_url_rule("/search-suggestions/autosuggest",
    view_func=AutoSuggest.as_view("autosuggest"))

