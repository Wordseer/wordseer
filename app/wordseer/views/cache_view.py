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
        final_result = project.sentences
        sub_search_ids = []
        some_filtering_happened = False
        if 'phrases' in keys:
            sentence_query = self.apply_phrase_filters(params['phrases'][0],
                                                       sentence_query)
            some_filtering_happened = True
        if 'metadata' in keys:
            sentence_query = self.apply_property_filters(params['metadata'][0],
                                                         sentence_query)
            some_filtering_happened = True
        if 'search' in keys:
            search_params = loads(params['search'][0])
            final_result = self.apply_search_filters(search_params, sentence_query)
            if params["separate_sub_searches"] and len(search_params) > 1:
                for search in search_params:
                    search_query = Query()
                    search_query.sentences = self.apply_search_filter(
                        search, sentence_query)
                    search_query.save()
                    sub_search_ids.append(search_query.id)
            some_filtering_happened = True
        if some_filtering_happened:
            query.sentences = final_result
            query.save()
        return jsonify({
            "ok": True,
            "query_id": query.id,
            "sub_search_ids": sub_search_ids})

    def apply_search_filter(self, search_query_dict, filtered_sentences):
        if Query.is_grammatical_search_query(search_query_dict):
            filtered = Dependency.\
                apply_grammatical_search_filter(search_query_dict,
                    filtered_sentences)
        else:
            filtered = Word.apply_non_grammatical_search_filter(
                search_query_dict, filtered_sentences)
        return filtered

    def apply_search_filters(self, search_params, filtered_sentences):
        """ Add filters to the given query to restrict to just the sentences
        matched by the text and grammatical searches issued.
        """
        for search_query_dict in search_params:
            filtered_sentences = self.apply_search_filter(search_query_dict,
                                                          filtered_sentences)
        return filtered_sentences

    def apply_phrase_filters(self, phrase_filters_string, filtered_sentences):
        """ Add filters to the given query to restrict to just the sentences
        that contain the specified phrases.
        """
        json_parsed_phrase_filters = loads(phrase_filters_string)
        matching_sentences = None
        for phrase_filter in json_parsed_phrase_filters:
            # Each phrase filter has the format <word|phrase>_<id>_surface
            components = phrase_filter.split("_")
            if components[0] == "phrase":
                sequence_id = components[1]
                sequence = Sequence.query.get(sequence_id)
                matching_sentences = db.session.query(
                    SequenceInSentence.sentence_id).filter(
                    SequenceInSentence.sequence_id == sequence.id).subquery()
            elif components[0] == "word":
                word_id = components[1]
                word = Word.query.get(word_id)
                if "." in word_id:
                    # Indicates that we should use the lemmatized form
                    # see views/words_view.py
                    word_id = word_id.replace(".", "")
                    word = Word.query.get(word_id)
                    matching_sentences = db.session.query(
                        WordInSentence.sentence_id).\
                    join(Word, WordInSentence.word_id == Word.id).\
                    filter(Word.lemma == word.lemma).subquery()
                else:
                    matching_sentences = db.session.query(
                        WordInSentence.sentence_id).\
                    filter(WordInSentence.word_id == word.id).subquery()


            filtered_sentences = filtered_sentences.join(
                matching_sentences,
                Sentence.id == matching_sentences.c.sentence_id)
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
            components = identifier.split("_")
            type = components[0]
            property_name = "_".join(components[1:])
            matching_sentences = None
            if type == "string":
                values = []
                for value_expression in value_list:
                    (text, value) = value_expression.split("__")
                    values.append(value)
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
