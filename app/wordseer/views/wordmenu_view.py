from flask.views import MethodView
from flask.json import jsonify, dumps, loads
from flask import request
from sqlalchemy import func
from sqlalchemy.sql.expression import asc, desc

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class GrammaticalSearchOptionsView(MethodView):

    def get_relationship_group(self, relationship):
        for group in GRAMMATICAL_RELATION_GROUPS:
            if relationship + " " in group or " " + relationship in group:
                return group
        return relationship

    def add_relation_to_response(self, response, relation_type, relation):
        if relation.relationship is None:
            return
        group = self.get_relationship_group(relation.relationship)
        if relation_type not in response:
            response[relation_type] = {}
        if group not in response[relation_type]:
            response[relation_type][group] = {"count" : 0, "children": {}}
        response[relation_type][group]["children"][relation.word] = relation.count
        response[relation_type][group]["count"] += relation.count

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        project = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
        if project is None:
            return
        word_ids = Word.get_matching_word_ids(params.get("word")[0],
            is_set_id = params.get("class")[0] == "phrase-set")

        deps = db.session.query(
            GrammaticalRelationship.name.label("relationship"),
            Word.surface.label("word"),
            func.count(DependencyInSentence.sentence_id).label("count")).\
        join(Dependency, Dependency.dependent_id == Word.id).\
        filter(GrammaticalRelationship.project_id == project.id).\
        filter(GrammaticalRelationship.id ==
            Dependency.grammatical_relationship_id).\
        filter(Dependency.governor_id.in_(word_ids)).\
        filter(DependencyInSentence.dependency_id == Dependency.id).\
        group_by(GrammaticalRelationship.name, Word.surface)

        govs = db.session.query(
            GrammaticalRelationship.name.label("relationship"),
            Word.surface.label("word"),
            func.count(DependencyInSentence.sentence_id).label("count")).\
        join(Dependency, Dependency.governor_id == Word.id).\
        filter(GrammaticalRelationship.project_id == project.id).\
        filter(Dependency.dependent_id.in_(word_ids)).\
        filter(GrammaticalRelationship.id ==
               Dependency.grammatical_relationship_id).\
        filter(DependencyInSentence.dependency_id == Dependency.id).\
        group_by(GrammaticalRelationship.name, Word.surface)

        response = {}
        for relation in deps:
            self.add_relation_to_response(response, "gov", relation);
        for relation in govs:
            self.add_relation_to_response(response, "dep", relation);

        response["search"] = WordInSentence.query.\
            filter(WordInSentence.project_id == project.id).\
            filter(WordInSentence.word_id.in_(word_ids)).count()

        return jsonify(response)



GRAMMATICAL_RELATION_GROUPS = [
    "amod advmod acomp",
    "agent subj nsubj xsubj csubj nsubjpass csubjpass",
    "dobj iobj pobj",
    "prep_because prep_because_of prep_on_account_of prep_owing_to prepc_because prepc_because_of prepc_on_account_of prepc_owing_to",
    "conj_and",
    "prep_with prepc_with prep_by_means_of prepc_by_means_of",
    "prep pobj",
    "prep_to",
    "prep_from",
    "prep_of",
    "prep_on",
    "prep_by",
    "prep_in",
    "abbrev",
    "acomp",
    "advcl",
    "advmod",
    "agent",
    "amod",
    "appos",
    "attr",
    "aux",
    "auxpass",
    "cc",
    "ccomp",
    "complm",
    "conj",
    "cop",
    "csubj",
    "csubjpass",
    "dep",
    "det",
    "dobj",
    "expl",
    "infmod",
    "iobj",
    "mark",
    "mwe",
    "neg",
    "nn",
    "npadvmod",
    "nsubj",
    "nsubjpass",
    "num",
    "number",
    "parataxis",
    "partmod",
    "pcomp",
    "pobj",
    "poss",
    "preconj",
    "predet",
    "prep",
    "prepc",
    "prt",
    "punct",
    "purpcl",
    "quantmod",
    "rcmod",
    "ref",
    "rel",
    "root",
    "tmod",
    "xcomp",
    "xsubj"]


register_rest_view(
    GrammaticalSearchOptionsView,
    wordseer,
    'wordmenu_view',
    'grammatical_search_option',
    parents=["project"],
)