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
        return self.dispatch(params)

    def dispatch(self, params):
        if "clear" in params:
            return self.clear_old_query(params)
        else:
            return self.new_query(params)

    def clear_old_query(self, params):
        query = Query.query.get(params["query_id"])
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
            sentence_query = self.apply_search_filters(params['search'][0],
                                                       sentence_query)
            some_filtering_happened = True
        if 'phrases' in keys:
            sentence_query = self.apply_phrase_filters(params['phrases'][0],
                                                       sentence_query)
        if 'metadata' in keys:
            sentence_query = self.apply_property_filters(params['metadata'][0],
                                                         sentence_query)
        if some_filtering_happened:
            query.sentences = sentence_query
            query.save()
        return jsonify({ "ok": True, "query_id": query.id })

    def apply_search_filters(self, search_string, filtered_sentences):
        """ Add filters to the given query to restrict to just the sentences
        matched by the text and grammatical searches issued.
        """
        json_parsed_search_params = loads(search_string)
        for search_query_dict in json_parsed_search_params:
            if Query.is_grammatical_search_query(search_query_dict):
                filtered_sentences = Sentence.\
                    apply_grammatical_search_filter(search_query_dict,
                        filtered_sentences)
            else:
                filtered_sentences = Word.apply_non_grammatical_search_filter(
                    search_query_dict, filtered_sentences)
        return filtered_sentences

    def apply_phrase_filters(self, phrase_filters_string, filtered_sentences):
        """ Add filters to the given query to restrict to just the sentences
        that contain the specified phrases.
        """
        json_parsed_phrase_filters = loads(phrase_filters_string)
        for phrase_filter in json_parsed_phrase_filters:
            # Each phrase filter has the format <word|phrase>_<id>_surface
            components = phrase_filter.split("_")
            sequence_id = components[1]
            sequence = Sequence.query.get(sequence_id)
            matching_sentences = SequenceInSentence.query.filter(
                SequenceInSentence.sequence_id == sequence_id).subquery()
            filtered_sentences = filtered_sentences.join(
                matching_sentences,
                matching_sentences.c.sentence_id == Sentence.id)
        return filtered_sentences

    def apply_property_filters(self, property_filters_string,
        filtered_sentences):
        """ Add filters to the given query to restrict to just the sentences
        that contain the specified property values.
        """
        property_filters = loads(property_filters_string)
        for identifier, value_list in property_filters.iteritems():
            # Identifiers have the format "<type>_<property_name>".
            # Values have the format "text__value" for string properties
            # They have the format [start_value, end_value] for number and
            # date properties.
            (type, property_name) = identifier.split("_")
            print property_name
            matching_sentences = None
            if type == "string":
                values = []
                for value_expression in value_list:
                    (text, value) = value_expression.split("__")
                    values.append(value)
                    print value
                matching_sentences = db.session.query(
                    PropertyOfSentence.sentence_id.label("sentence_id")).\
                join(Property, PropertyOfSentence.property_id == Property.id).\
                filter(Property.name == property_name).\
                filter(Property.value.in_(values)).subquery()
            else:
                for values in value_list:
                    matching_sentences = db.session.query(
                        PropertyOfSentence.sentence_id.label("sentence_id")).\
                    join(Property, PropertyOfSentence.property_id == Property.id).\
                        filter(Property.name == property_name).\
                        filter(Property.value >= values[0]).\
                        filter(Property.value <= values[1]).\
                        subquery()
            filtered_sentences = filtered_sentences.join(
                matching_sentences,
                Sentence.id == matching_sentences.c.sentence_id)
            return filtered_sentences

    def put(self, id):
        pass


register_rest_view(
    QueryCacheView,
    wordseer,
    'cache_view',
    'cache',
    pk="query_id",
    parents=["project"]
)
