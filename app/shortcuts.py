"""
Various methods helpful in the wordseer flask app.
"""

import exceptions

def really_submitted(form):
    """ WTForms can be really finnicky when it comes to checking if a form
    has actually been submitted, so this method runs validate_on_submit()
    on the given form and checks if its "submitted" field has any data. Useful
    for pages that have two forms on them.

    :arg Form form: A form to check for submission.
    :returns boolean: True if submitted, false otherwise.
    """

    return form.validate_on_submit() and form.submitted.data

def get_object_or_404(model, attribute, value, exception=None):
    """Either get the requested object or raise an exception.

    :arg model model: The Model of the requested object.
    :arg attribute: The attribute of the Model of the requested object.
    :arg value: The required value of the attribute.
    :arg exception: The exception to raise on failure.
    """
    
    #FIXME, see issue tracker
    try:
        session.query(model).filter(attribute == value).one()
    except NoResultFound:
        try:
            raise exception
        except:
            abort(404)
