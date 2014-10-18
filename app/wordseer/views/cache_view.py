from flask import request
from flask.json import jsonify, dumps, loads
from flask.views import MethodView

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class QueryCacheView(MethodView):


    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        self.dispatch(params)

    def dispatch(self, params):
        if params["clear"]:
            self.clear_old_query(params)
        else:
            self.new_query(params)

    def clear_old_query(self, params):
        query = Query.get(params["cache_id"])
        if query:
            query.delete()
            return jsonify({ "ok": True })
        else:
            return jsonify({ "ok": False })

    def new_query(self, params):
        project = Project.query.get(params["project_id"])
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

    def put(self, id):
        pass


register_rest_view(
    QueryCacheView,
    wordseer,
    'cache_view',
    'cache',
    parents=["project"]
)
