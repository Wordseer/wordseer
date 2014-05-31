"""This file contains utilities for finding grammatical patterns within
two positions in a given sentence.
"""

from flask import request
from flask.json import jsonify

from app import db
from ...uploader.models import Dependency
from ...uploader.models import Sentence
from .. import wordseer

@wordseer.route("/getpatterns")
def get_patterns():
    sentence = request.args.get("sentence")
    start = request.args.get("start")
    end = request.args.get("end")
    dependencies = []

    if sentence and start and end:
        dependencies = db.session.query(Dependency).join(Sentence).\
            filter(Sentence.id == sentence).\
            filter(Dependency.gov_index <= end).\
            filter(Dependency.dep_index <= end).\
            filter(Dependency.gov_index >= start).\
            filter(Dependency.dep_index >= start).all()

    elif sentence:
        dependencies = db.session.query(Dependency).join(Sentence).\
            filter(Sentence.id == sentence).all()

    information = []

    for dependency in dependencies:
        if dependency.relationship != "dep":
            #FIXME: mysterious fields, gov_id?
            information.append({
                "id": dependency.id,
                "gov": dependency.governor,
                #"gov_id": dependency.gov_id,
                "dep": dependency.dependent,
                #"dep_id": dependency.dep_id,
                "relation": dependency.relationship
            })

    return jsonify(information)

