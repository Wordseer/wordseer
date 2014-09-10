"""Mixins for the database models.
"""

from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty

class NonPrimaryKeyEquivalenceMixin(object):
    """A mixin for models that should be compared by their non-primary key
    fields.
    """
    def __eq__(self, other):
        """If all non-primary key fields of these objects are the same, then
        these objects are equivalent. Borrwed from sqlachemy-utils.
        """
        for prop in inspect(other.__class__).iterate_properties:
            if not isinstance(prop, ColumnProperty):
                continue

            if prop.columns[0].primary_key:
                continue

            if not getattr(other, prop.key) == getattr(self, prop.key):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

