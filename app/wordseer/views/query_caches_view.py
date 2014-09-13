from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class QueryCachesView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        query = QueryCache()
        query.save()

        return jsonify({ "ok": True, "query_id": query.id })

    def post(self):
        pass

    def delete(self, id):

        query_cache = QueryCache.query.get(id)

        if query_cache:
            query_cache.delete()
        else:
            print("No query found")

    def put(self, id):
        pass


register_rest_view(
    QueryCachesView,
    wordseer,
    'query_caches_view',
    'query_cache',
    parents=["project"]
)
