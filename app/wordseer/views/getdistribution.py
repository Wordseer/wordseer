"""This module contains utilities for finding all the occurrences
of given grammatical patterns or a textual pattern in a given narrative.
"""

from flask import request
from flask import abort
from flask.json import jsonify
from flask.views import View
from sqlalchemy.sql import func

from app import app
from app import db
from .. import wordseer
from ...uploader.models import Dependency
from ...uploader.models import dependency_in_sentence
from ...uploader.models import Sentence
from ...uploader.models import Unit

@wordseer.route("/getdistribution")
def get_distribution():
    """Return the JSON response for this view.
    """
    narrative = request.args.get("narrative")
    distribution_type = request.args.get("type") # grammatical or text?

    if not narrative or not distribution_type:
        abort(400)

    row = get_dimensions(narrative)

    ocurrences = {
        "total": row.length,
        "min":  row.min,
        "max": row.max,
        "narrative": narrative,
        "type": distribution_type,
    }

    if distribution_type == "grammatical":
        ids = request.args.get("id")
        ocurrences["instances"] = {}
        for id in ids:
            ocurrences["instances"][str(id)] = \
                get_grammatical_ocurrences(narrative, id)

    elif distribution_type == "text":
        ocurrences["original"] = request.args.get("q")
        ocurrences["instances"] = get_text_ocurrences(narrative, q)

    return jsonify(ocurrences)

def get_dimensions(narrative_id):
    """Return the number of sentences, minimum sentence id, and maximum
    sentence id in the given narrative.

    Arguments:
        narrative_id (int): The int of the narrative to retrieve info for.

    Returns:
        KeyedTuple: A KeyedTuple with the items ``length``, ``min``, and
            ``max``, respectively containing the number of sentences, the
            minimum present sentence ID, and the maximum present sentence
            ID.
    """

    #FIXME: what is narrative?
    result = db.session.query(
        func.min(Sentence.id).label("min"),
        func.max(Sentence.id).label("max"),
        func.count(Sentence.id).label("length")).\
            join(Unit).\
            filter(Unit.id == narrative_id).one()

    return result

def get_grammatical_ocurrences(narrative_id, dependency_id):
    """Return a list of Sentences from the given narrative in which
    the given dependency ID occurs.

    Arguments:
        narrative_id (int): The ID of the narrative the Sentences should
            have.
        dependency_id (int): The ID of the dependency the Sentences should
            have.

    Returns:
        list: A list of Sentence objects meeting the above criteria.
    """
    #TODO: what is narrative?

    result = db.session.query(Sentence).\
        join(dependency_in_sentence, Unit).\
        filter(Unit.id == narrative_id).\
        filter(Dependency.id == dependency_id).\
        order_by(Sentence.id).\
        all()

    return result

def get_text_occurrences(narrative_id, pattern):
    """Return a list of Sentences from the given narrative in which the
    given pattern occurs exactly.

    Arguments:
        narrative_id (int): The ID of the narrative the Sentences should
            have.
        pattern (str):

    Returns:
        list: A list of Sentence objects meeting the above criteria.
    """

    sentences = db.session.query(Sentence).join(Unit).\
        filter(Unit.id == narrative_id).\
        filter(Sentence.text.match(pattern)).\
        order_by(Sentence.id).all()

    return sentences

