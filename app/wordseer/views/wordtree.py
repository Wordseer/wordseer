from flask import abort
from flask import request
from flask.json import jsonify, loads
from flask.views import MethodView
from sqlalchemy import func
from sqlalchemy.sql.expression import desc
from nltk import word_tokenize

from app import db
from app.models.user import User
from app.models import *
from app.wordseer import wordseer

from app.helpers.application_view import register_rest_view


class WordTreeView(MethodView):
    def __init__(self):
        self.query = None

    def get_center_strings_from_search(self, searches, wordtree_center_strings):
        if len(searches) == 0:
            return []
        search = searches[-1]
        if "gov" in search:
            sequence_ids = Word.get_matching_sequence_ids(
                search["gov"],
                is_set_id = search["govtype"] != "word")
            for sequence_id in sequence_ids:
                wordtree_center_strings.append(
                    Sequence.query.get(sequence_id).sequence)
            if search["govtype"] != "word":
                self.query = SequenceSet.query.get(search["gov"]).name
            else:
                self.query = wordtree_center_strings[-1]
                
        return wordtree_center_strings

    def get_center_strings_from_phrase_filters(self, phrase_filters,
        wordtree_center_strings):
        if len(phrase_filters) == 0:
            return []
        phrase_filter = phrase_filters[-1]
        components = phrase_filter.split("_")
        if len(components) != 3:
            abort(500)
        if components[0] == "phrase":
            wordtree_center_strings.append(
                Sequence.query.get(components[1]).sequence)
            self.query = wordtree_center_strings[-1]
        elif components[0] == "word":
            word_id = components[1]
            if "." in word_id:
                word_id = word_id.replace(".", "")
                word = Word.query.get(word_id)
                words = Word.query.filter(Word.lemma == word.lemma)
                for word in words:
                    wordtree_center_strings.append(word.surface)
                    self.query = word.surface
            else:
                word = Word.query.get(word_id)
                wordtree_center_strings.append(word.word)
                self.query = word.word
        return wordtree_center_strings

    def get_center_strings_from_metadata(self, query, metadata_filters,
        wordtree_center_strings):
        if "string_phrase_set" in metadata_filters:
            for value_expression in metadata_filters["string_phrase_set"]:
                (text, value) = value_expression.split("__")
                set = SequenceSet.query.get(value)
                if set is not None:
                    self.query = set.name
                    for sequence in set.sequences:
                        wordtree_center_strings.append(
                            sequence.sequence)
        else:
            top_word = db.session.query(
                Word.surface.label("surface"),
                func.count(
                    WordInSentence.sentence_id.distinct()).label("count")).\
            join(SentenceInQuery,
                SentenceInQuery.sentence_id == WordInSentence.sentence_id).\
            filter(WordInSentence.word_id == Word.id).\
            filter(SentenceInQuery.query_id == query.id).\
            filter(Word.part_of_speech.like("N%")).\
            group_by(Word.surface).\
            order_by(desc("count")).first()
            wordtree_center_strings.append(top_word.surface)
            self.query = top_word.surface
        return wordtree_center_strings


    def get_center_strings(self, query, params):
        keys = params.keys()
        wordtree_center_strings = []
        if "search" in keys:
            searches = loads(params["search"][0])
            wordtree_center_strings = self.get_center_strings_from_search(
                searches,
                wordtree_center_strings)
        if "phrases" in keys and len(wordtree_center_strings) == 0:
            phrase_filters = loads(params["phrases"][0])
            wordtree_center_strings = self.get_center_strings_from_phrase_filters(
                phrase_filters, wordtree_center_strings)
        if "metadata" in keys and len(wordtree_center_strings) == 0:
            metadata_filters = loads(params["metadata"][0])
            wordtree_center_strings = self.get_center_strings_from_metadata(
                query, metadata_filters, wordtree_center_strings)
        return wordtree_center_strings


    def get(self, **kwargs):
        self.query = None
        params = dict(kwargs, **request.args)
        keys = params.keys()
        project = None
        query = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
            if "query_id" in keys:
                query = Query.query.get(params["query_id"])
        if project is None or query is None:
            abort(500)

        wordtree_center_strings = self.get_center_strings(query, params)
        if len(wordtree_center_strings) == 0:
            return
        sentences = query.sentences;
        tree_data = {
            "query": self.query,
            "concordance": {
                "lefts":[],
                "rights": [],
                "num": len(sentences)
            }
        }
        center_string_token_lists = [map(lambda x: x.lower(), word_tokenize(center_string)) 
            for center_string in wordtree_center_strings]
        for sentence in query.sentences:
            left = {"id": sentence.id, "sentence": []}
            right = {"id": sentence.id, "sentence": []}

            tokens = map(lambda x: x.lower(), word_tokenize(sentence.text))
            matched = False
            for center_string_token_list in center_string_token_lists:
                if not matched:
                    for start_index in range(len(tokens) - len(center_string_token_list)):
                        candidate = tokens[start_index : start_index + len(center_string_token_list)]
                        if candidate == center_string_token_list:
                            lefts = tokens[:start_index]
                            lefts.reverse()
                            left["sentence"] = lefts
                            right["sentence"] = tokens[start_index + len(center_string_token_list) : ]
                            matched = True
                            break
            tree_data["concordance"]["lefts"].append(left)
            tree_data["concordance"]["rights"].append(right)

        return jsonify(tree_data)


register_rest_view(
    WordTreeView,
    wordseer,
    'wordtree',
    'wordtree',
    parents=["project"],
)