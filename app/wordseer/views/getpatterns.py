"""Finding grammatical patterns within two positions in a given sentence.
"""

from flask import request
from flask import abort
from flask.json import jsonify

from app import db
from ...uploader.models import Dependency
from ...uploader.models import dependency_in_sentence
from ...uploader.models import Sentence
from .. import wordseer

@wordseer.route("/getpatterns")
def get_patterns():
    """Get a JSON object representing the dependencies matching the given
    criteria.

    The JSON object is formatted like this::

        {
            "results": [
                {
                    "id": int, < ID of this dependency
                    "gov": str, < The governor
                    "gov_id": int,
                    "dep": str, < The dependent
                    "dep_id": int,
                    "relation": str < The relationship described
                }
                ...and so on...
            ]
        }

    Keyword Arguments:
        sentence (int): The ID of the sentence whose dependencies should
            be queried. Required.
        start (int): The minimum index (inclusive) of either word in the
            dependency.
        end (int): The maximum index (inclusive) of either word in the
            dependency.

    Returns:
        If all goes well, a JSON string is returned with the above structure.
        If a parameter is not properly given, a 400 error will occur. If there
        is another error, a 500 error will occur.
    """

    try:
        sentence = int(request.args["sentence"])
    except (ValueError, KeyError):
        abort(400)

    start = int(request.args.get("start", -1))
    end = int(request.args.get("end", -1))
    dependencies = []

    if sentence and start > -1 and end > -1:
        dependencies = db.session.query(Dependency).\
            join(dependency_in_sentence).\
            filter(Sentence.id == sentence).\
            filter(Dependency.gov_index <= end).\
            filter(Dependency.dep_index <= end).\
            filter(Dependency.gov_index >= start).\
            filter(Dependency.dep_index >= start).all()

    elif sentence:
        dependencies = db.session.query(Dependency).\
            join(dependency_in_sentence).\
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

    return jsonify(results=information)

