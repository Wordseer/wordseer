"""
A mixin to convert kwargs to attributes.
"""

class KwargsToDict(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)