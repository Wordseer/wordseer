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
    """Returns data that backs the Metadata Frequencies view for a set of
    results."""

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)        
        query = Query.query.get(params["query_id"])
        keys = params.keys()
        metadata_counts = {}
        header = ["x"]
        if "search" in keys:
            search_params = loads(params["search"][0])
            if len(search_params) > 1:
                for i, search_param in enumerate(search_params):
                    header.append(str(i))
                    add_query_counts_to_results(
                        metadata_counts, len(search_params), i,
                        search_param.query_id)

            else:
                header.append(0)
                self.add_query_counts_to_results(metadata_counts, 1, 0, query.id)

        results = {}
        for property, counts in metadata_counts.iteritems():
            results[property] = {
             "sentences": [header],
             "totals": [["x", "total"]]
             }
            for value, query_counts in counts.iteritems():
                results[property]["sentences"].append(query_counts[1:])
                results[property]["totals"].append(
                    [value, len(query_counts[0])])
        return jsonify(results)

    def add_query_counts_to_results(
        self, results, num_queries, query_index, query_id):
        query = Query.query.get(query_id)
        for sentence in query.sentences:
            for property in sentence.properties:
                if property.name not in results:
                    results[property.name] = {}
                if property.value not in results[property.name]:
                    values = [set(), property.value]
                    values.extend([0] * num_queries)
                    results[property.name][property.value] = values
                results[property.name][property.value][2 + query_index] += 1
                results[property.name][property.value][0].add(sentence.id)

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
