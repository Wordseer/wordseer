"""
Custom defined widgets for this flask app.
"""

from cgi import escape

from wtforms.widgets import html_params, HTMLString

class ButtonWidget(object):
    """A widget to conveniently display buttons.
    """
    def __call__(self, field, **kwargs):
        if field.name is not None:
            kwargs.setdefault('name', field.name)
        if field.value is not None:
            kwargs.setdefault('value', field.value)
        kwargs.setdefault('type', "submit")
        return HTMLString('<button %s>%s</button>' % (
            html_params(**kwargs),
            escape(field._value())
            ))
