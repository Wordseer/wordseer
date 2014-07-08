"""
A mixin to convert kwargs to attributes.
"""

class KwargsToDict(object):
    """This mixin converts kwargs passed to the constructor to attributes.
    """
    def __init__(self, **kwargs):
        """When a class is created, automatically convert its kwargs to
        attributes.
        :param dict kwargs: The keyword arguments passed to the class.
        """

        for key, value in kwargs.items():
            setattr(self, key, value)
