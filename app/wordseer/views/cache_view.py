from flask import request
from flask.json import jsonify, dumps, loads
from flask.views import MethodView

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class QueryCacheView(MethodView):

    def apply_search_filters(self, search_string, filtered_sentences):
        json_parsed_search_params = loads(search_string)
        for search_query_dict in json_parsed_search_params:
            if Query.is_grammatical_search_query(search_query_dict):
                filtered_sentences = Sentence.apply_grammatical_search_filter(
                    search_query_dict, filtered_sentences)
            else:
                filtered_sentences = Sentence.apply_non_grammatical_search_filter(
                    search_query_dict, filtered_sentences)
        return filtered_sentences


    def get(self, **kwargs):
        project = Project.query.get(kwargs["project_id"])
        params = dict(kwargs, **request.args)
        keys = params.keys()
        query = Query()
        query.save()
        sentence_query = project.sentences
        some_filtering_happened = False
        if 'search' in keys:
            some_filtering_happened = True
            sentences = self.apply_search_filters(params['search'][0],
                sentence_query)
        if (some_filtering_happened):
            query.sentences = sentence_query
            query.save()
        return jsonify({ "ok": True, "query_id": query.id })

    def post(self):
        pass

    def delete(self, id):

        query_cache = Query.get(id)

        if query_cache:
            query_cache.delete()
        else:
            print("No query found")

    def put(self, id):
        pass


register_rest_view(
    QueryCacheView,
    wordseer,
    'cache_view',
    'cache',
    parents=["project"]
)
