from flask.views import MethodView
from flask.json import jsonify, dumps, loads
from flask import request
from nltk import word_tokenize

from app import app
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view
from app.wordseer.helpers import parse_phrase_strings

class MetadataFrequenciesView(MethodView):
    """Returns data that backs the Metadata Profile view for a set of
    results."""

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        query = Query.query.get(params["query_id"])
        keys = params.keys()
        metadata_counts = {}
        header = ["x"]
        if "search" in keys:
            search_params = loads(params["search"][0])
            for i, search_param in enumerate(search_params):
                query_text = search_param['gov']
                if search_param['relation'] != "":
                    query_text += ", %s (%s)" % (search_param['dep'],
                        search_param['relation'])
                header.append(query_text)
                self.add_query_counts_to_results(
                    metadata_counts, len(search_params), i,
                    search_param['query_id'], params["project_id"])

        results = {}
        for property, counts in metadata_counts.iteritems():
            prop_obj = Property.query.filter(Property.name == property,
                Property.project_id == params["project_id"]).first()

            results[property] = {
                "sentences": [header],
                "totals": [["x", "total"]],
                "datatype": prop_obj.property_metadata.data_type
            }

            if results[property]['datatype'] == "date":
                results[property]['date_format'] = prop_obj.property_metadata.date_format

            for value, query_counts in counts.iteritems():
                results[property]["sentences"].append(query_counts[1:])
                results[property]["totals"].append(
                    [value, query_counts[0]])

        return jsonify(results)

    def add_query_counts_to_results(
        self, results, num_queries, query_index, query_id, project_id):
        query = Query.query.get(query_id)
        for sentence in query.sentences:
            for property in sentence.properties:
                if property.name not in results:
                    results[property.name] = {}
                if property.value not in results[property.name]:
                    total = 0

                    # need to aggregate any duplicate props
                    # that are associated with different unit_ids
                    for prop in Property.query.filter(
                        Property.name == property.name,
                        Property.value == property.value,
                        Property.project_id == project_id
                    ):
                        total += len(prop.sentences_with_property)

                    values = [total, property.value]
                    values.extend([0] * num_queries)
                    results[property.name][property.value] = values
                results[property.name][property.value][2 + query_index] += 1

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass

register_rest_view(
    MetadataFrequenciesView,
    wordseer,
    'metdata_frequencies_view',
    'metadata_frequency',
    parents=["project"]
)
