import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class Caching(View):
    """Utilities for caching the the sentences, phrases, and documents
    that match a query."""

    def make_cache_tables():
        """Creates tables to cache the results of applying the filters
        for this query."""
        pass

    def dispatch_clear_query_cache(query_id):
        pass

    def dispatch_caching(searches, collection, metadata, phrases):
        """Does the filtering operations necessary for the query and
        prints out a new query ID."""
        pass

    def get_next_query_id():
        pass
