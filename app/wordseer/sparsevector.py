"""
A vector space model for finding similar sentences.
"""

class SparseVector(object):
    """A vector space model used by the Rocchio algorithm.
    """

    def __init__(self, feature_list={}):
        """Initialize a SparseVector.

        Arguments:
            feature_list (dict): A dictionary containing the features of this
                vector in the format ``{id: value}``, where ``value`` is an
                ``int``.
        """
        self.features = feature_list

    def __add__(self, other):
        """Add this vector to other.

        Arguments:
            other (SparseVector): A vector to add to this one.

        Returns:
            SparseVector: the result of the summing.
        """

        result = {}
        for feature_id, feature_value in self.features.iteritems():
            result[feature_id] = feature_value

        for feature_id, feature_value in other.features.iteritems():
            try:
                result[feature_id] += feature_value
            except KeyError:
                result[feature_id] = feature_value

        return SparseVector(result)

    def __mul__(self, other):
        """Multiply this vector by the other as a dot product.

        Arguments:
            other (SparseVector): The vector to multiply by.

        Returns:
            SparseVector: The result of the multiplication.
        """

        dot_product = 0
        for feature_id, other_feature_value in other.features.iteritems():
            try:
                dot_product += (self.features[feature_id] * \
                        other_feature_value)
            except KeyError:
                pass
        return dot_product

    def __rmul__(self, other):
        """Multiply this vector by other, a scalar value.

        Arguments:
            other (scalar): The scalar to multiply by.

        Returns:
            SparseVector: This SparseVector, with a scalar multiplication
                applied.
        """

        result = {}

        for feature_id, feature_value in self.features.iteritems():
            result[feature_id] = feature_value * other

        return SparseVector(result)

    def normalize(self):
        """Return the normalized (unit vector) version of this vector, that
        is, all the components (features) sum to 1.

        Returns:
            SparseVector: the unit vector for this vector.
        """

        unit_features = {}
        total = 0

        total = sum(self.features.values())

        for feature_id, feature_value in self.features.iteritems():
            unit_features[feature_id] = feature_value / float(total)

        return SparseVector(unit_features)

    def __eq__(self, other):
        """Check if this SparseVector is equivalent to another one.


        Returns:
            boolean: If ``other`` has a ``features`` attribute that is
                identical to this object's ``features`` attribute, then
                ``True``. otherwise, ``False``.
        """

        try:
            return self.features == other.features
        except AttributeError:
            return False

    def __str__(self):
        """Give a string representation of this object.
        """

        return "SparseVector <" + str(self.features) + ">"

