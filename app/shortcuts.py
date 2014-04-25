"""
Various methods helpful in the wordseer flask app.
"""

from flask import render_template, abort
from sqlalchemy.orm.exc import NoResultFound

import exceptions
from models import session

def really_submitted(form):
    """ WTForms can be really finnicky when it comes to checking if a form
    has actually been submitted, so this method runs validate_on_submit()
    on the given form and checks if its "submitted" field has any data. Useful
    for pages that have two forms on them.

    :arg Form form: A form to check for submission.
    :returns boolean: True if submitted, false otherwise.
    """

    if form.submitted.data == "true":
        return form.validate_on_submit()
    return False

def get_object_or_exception(model, attribute, value, exception=None):
    """Either get the requested object or raise an exception.

    :arg model model: The Model of the requested object.
    :arg attribute: The attribute of the Model of the requested object.
    :arg value: The required value of the attribute.
    :arg exception: The exception to raise on failure.
    """
    
    #FIXME, see issue tracker
    try:
        return session.query(model).filter(attribute == value).one()
    except NoResultFound:
        try:
            raise exception
        except:
            abort(404)

def not_found(item):
    """Render the item_not_found.html template with item set to the given item,
    and return a 404 code.

    :arg str item: The name of the item not found.
    """
    return render_template("item_not_found.html", item=item), 404
