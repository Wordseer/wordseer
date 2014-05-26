"""This module contains utilities for finding all the occurrences
of given grammatical patterns or a textual pattern in a given narrative.
"""

from flask import request
from flask.json import JSONDecoder
from flask.json import JSONEncoder
from flask.views import View

from app import app

class GetDistribution(View):
    def dispatch(self):
        ocurrences = {}
        narrative = request.args.get("narrative")
        row = self.get_dimensions(narrative)
        ocurrences["total"] = row.length
        ocurrences["min"] = row.min
        ocurrences["max"] = row.max
        ocurrences["narrative"] = narrative

        distribution_type = request.args.get("type") # grammatical or text?
        ocurrences["type"] = distribution_type

        if distribution_type == "grammatical":
            ids = request.args.get("id")
            ocurrences["instances"] = {}
            for id in ids:
                ocurrences["instances"][str(id)] =
                    self.get_grammatical_ocurrences(narrative, id)

        elif distribution_type == "text":
            ocurrences["original"] = request.args.get("q")
            ocurrences["instances"] = get_text_ocurrences(narrative, q)

        return JSONEncoder(ocurrences)

    def get_dimensions(narrative_id):
        """Return the number of sentences, minimum sentence id, and maximum
        sentence id in the given narrative.

        Arguments:
            narrative_id (int): The int of the narrative to retrieve info for.

        Returns:
            dict: A dict with the items ``length``, ``min``, and ``max``,
                respectively containing the number of sentences, the minimum
                present sentence ID, and the maximum present sentence ID.
        """

