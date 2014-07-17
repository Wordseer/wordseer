"""
A mixin for classes all compared the same way.
"""

class CompareByDict(object):
    """A mixin for classes that should be compared by their attribute/value
    pairs. Useful for the Document classes.
    """

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __neq__(self, other):
        return self.__dict__ != other.__dict__
