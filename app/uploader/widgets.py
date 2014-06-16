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
        icon = kwargs.pop("icon", None)
        icon_span = ""
        if icon is not None:
            icon_span = "<span class='glyphicon " + icon + " '></span> "
        return HTMLString('<button %s>%s%s</button>' % (
            html_params(**kwargs),
            icon_span,
            escape(field._value())
            ))
