"""????
"""

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import MethodView
from sqlalchemy import not_
from sqlalchemy import func
from sqlalchemy.sql.expression import asc, desc
from sqlalchemy.sql.expression import literal_column

from app.wordseer import wordseer
from app import db
from app.models import *
from app.helpers.application_view import register_rest_view


# TODO: update existing code, refactor

class AutoSuggest(MethodView):
    """Retrieve a list of suggested ``Set``\s, ``Sequence``\s, and
    ``Property``\s.
    """
    def get(self, **kwargs):
        """Return a JSON list of suggestions of phrases, sets, and metadata
        property values that match the query.

        The ``query`` will be queried using a ``LIKE`` clause with ``%`` on
        either side of the string; so the ``query`` could be anywhere
        in the suggestions.

        The returned list has a maximum of three types of suggestions: 
        ``Set``\s, ``Property``\s, and ``Sequence``\s. The response is formed
        like so::

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

        Returns:
            A JSON response, or a 400 error if ``user`` is not supplied.
        """
        params = dict(kwargs, **request.args)
        self.project = Project.query.get(params["project_id"])

        if "query" in params and len(params["query"]) > 0:
            query_string = params["query"][0]
            like_query = "%" + query_string + "%"
            self.set_name_filter = Set.name.like(like_query)
            self.property_value_filter = Property.value.like(like_query)
            self.sequence_filter = Sequence.sequence.like(query_string + "%")

            suggestions = self.get_suggested_sets()
            suggestions.extend(self.get_suggested_properties())
            suggestions.extend(self.get_suggested_sequences())

            return jsonify(results=suggestions)
        else:
            return "[]"

    def get_suggested_sets(self):
        """Return a list of dicts of suggestions of ``Set``\s that may
        match the query.

        The query queries both ``Sets`` and ``Property``\s.

        ``Set``\s are filtered on the following criteria:

        * Have the same ``user`` as the one given in the request
        * Contain the ``query`` from the url, if applicable

        ``Property``\s are filtered by the following criteria:

        * ``unit_name`` is equal to ``sentence``
        * ``value`` is equal to the ``id`` of the ``Set``
        * ``name`` is ``phrase_set``

        Returns:
            list of dicts: A list containing dicts with the following info:
            ::

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
        sets = db.session.query(Set.id,
            Property.name.label("text"),
            literal_column("'metadata'").label("class"),
            func.count(Property.unit_id.distinct()).label("unit_count")).\
                filter(Property.value == Set.id).\
                filter(Set.project == self.project).\
                filter(Property.name.like("%_set")).\
                filter(self.set_name_filter).\
                group_by(Set.name).\
                all()

        return [set._asdict() for set in sets]

    def get_suggested_properties(self):
        """Return a list of dicts of suggestions of ``Property``\s that
        match the query.

        The query queries both ``Property`` and ``PropertyMetadata``.

        ``Property``\s are filtered by the following criteria:

        * ``value`` contains the user's ``query``, if any
        * ``Property.name`` is equal to ``PropertyMetadata.property_name``
        * The ``Property`` is a category (``is_category`` is true for these
            ``Property``\s)
        * ``Property.name`` does not contain ``_set``.

        Returns:
            list of dicts: A list of dicts with the following info:
            ::

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
        metadata = db.session.query(
            PropertyMetadata.display_name,
            Property.name,
            Property.value,
            literal_column("'metadata'").label("class"),
            func.count(Property.unit_id.distinct()).label("unit_count")).\
                filter(self.property_value_filter).\
                filter(Property.metadata_id == PropertyMetadata.id).\
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

    def get_suggested_sequences(self):
        """Return a list of dicts of suggestions of ``Sequence``\s that
        match the query.

        ``Sequence``\s are filtered by the following criteria:

        * ``Sequence.sequence`` starts with ``query``

        Returns:
            list of dicts: A list of dicts with the following info:
            ::

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
        filter(SequenceInSentence.sequence_id == Sequence.id).\
        filter(self.sequence_filter).\
        group_by(Sequence.sequence).\
        order_by(desc("sentence_count")).\
        order_by(asc(Sequence.length)).\
        limit(50)

        sequence_list = {}
        for sequence in sequences:
            text = sequence.text.lower()
            print text
            if text not in sequence_list and text is not None:
                sequence_list[text] = 1
                suggested_sequences.append(sequence._asdict())

        return suggested_sequences

register_rest_view(
    AutoSuggest,
    wordseer,
    'searchsuggestions',
    'autosuggestion',
    parents=["project"]
)
