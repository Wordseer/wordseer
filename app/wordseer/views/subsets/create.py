"""Views for creating, reading, updating, and deleting subsets.
"""

from datetime import date

from flask import abort
from flask import jsonify

from ...models import User
from ..helpers import get_model_from_tablename

def create(username, set_name, set_parent, set_type):
    """Create a new subset with the given information.

    Arguments:
        user (str): The username of the ``User`` that should own this ``Set``
        set_name (str): The ``name`` for the set to be created.
        set_parent: TODO: what is this and what does it do?
        set_type (str): The tablename of set that should be created.

    Returns:
        On success, a JSON response like so::

            {
                "status": "ok",
                "id": int, ID of the newly created Set
                "date": str, date of creation of this Set
            }

        On failure, a 400 error will be returned.
    """

    user = User.query.filter(User.name == username).one()

    try:
        set_model = get_model_from_tablename(set_type)(user=user,
            name=set_name,
            date=date.today()
        )
    except TypeError:
        return abort(400)

    set_model.save()

    #TODO: updateMainMetadataCounts? what does that even do?
    return jsonify(
        {
            "status": "ok", #TODO: let's get rid of this, 200 code is ok
            "id": set_model.id,
            "date": str(set_model.date)
        }
    )

