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
            # convert the JS boolean to Python
            search_lemmas = params["search_lemmas"][0] == 'true'

            if len(query_string) == 0:
                return "[]"
            like_query = "%" + query_string + "%"
            self.set_name_filter = Set.name.like(like_query)
            self.property_value_filter = Property.value.like(like_query)
            self.sequence_filter = Sequence.sequence.like(query_string + "%")
            self.search_lemmas = search_lemmas

            suggestions = self.get_suggested_sets()
            suggestions.extend(self.get_suggested_properties())
            suggestions.extend(self.get_suggested_sequences())

            return jsonify(results= sorted(suggestions,
                key=lambda s: -1*s["sentence_count"]))
        else:
            return "[]"

    def get_suggested_sets(self):
        """Return a list of dicts of suggestions of ``Set``\s that may
        match the query.

        The query queries both ``Sets`` and ``Property``\s.

        ``Set``\s are filtered on the following criteria:

        * Have the same ``user`` as the one given in the request
        * Have the same ``project`` as the one given in the request
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
        sets = db.session.query(SequenceSet.id,
            Set.name.label("text"),
            Property.name.label("class"),
            func.count(Property.unit_id).label("sentence_count")).\
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

        * Has the same ``project`` as the one given in the request
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
            PropertyMetadata.property_name.label("name"),
            PropertyMetadata.display_name.label("display_name"),
            Property.value.label("value"),
            func.count(PropertyOfSentence.sentence_id.distinct()).label("sentence_count")).\
                filter(Property.project == self.project).\
                filter(self.property_value_filter).\
                filter(PropertyOfSentence.property_id == Property.id).\
                filter(Property.property_metadata_id == PropertyMetadata.id).\
                filter(PropertyMetadata.is_category == True).\
                filter(not_(Property.name.like("phrase_set"))).\
                group_by(Property.value).\
                limit(50).\
                all()

        for datum in metadata:
            name = datum.name
            if datum.display_name is not None:
                name = datum.display_name
            suggestion = {
                "class": "metadata",
                "sentence_count": datum.sentence_count,
                "property_name": name,
                "text": "%s: %s" % (name, str(datum.value)),
                "value": datum.value
            }
            suggested_metadata.append(suggestion)

        return suggested_metadata

    def get_suggested_sequences(self):
        """Return a list of dicts of suggestions of ``Sequence``\s that
        match the query.

        ``Sequence``\s are filtered by the following criteria:

        * Has the same ``project`` as the one given in the request
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
        lemmatized_vals = [False]
        if self.search_lemmas:
            lemmatized_vals.append(True)
        sequences = db.session.query(Sequence.id,
            Sequence.sequence.label("text"),
            Sequence.length,
            Sequence.lemmatized,
            literal_column("'phrase'").label("class"),
            func.count(SequenceInSentence.sentence_id).\
                label("sentence_count")
        ).\
        filter(Sequence.project == self.project).\
        filter(SequenceInSentence.sequence_id == Sequence.id).\
        filter(Sequence.lemmatized.in_(lemmatized_vals)).\
        filter(self.sequence_filter).\
        group_by(Sequence.sequence).\
        order_by(desc("sentence_count")).\
        order_by(asc(Sequence.length)).\
        limit(50)

        sequence_list = {}
        for sequence in sequences:
            text = sequence.text.lower()
            # print text
            if text not in sequence_list and text is not None:
                sequence_list[text] = 1
                suggested_sequences.append(sequence._asdict())

        return suggested_sequences

register_rest_view(
    AutoSuggest,
    wordseer,
    'searchsuggestions',
    'searchsuggestion',
    parents=["project"]
)
