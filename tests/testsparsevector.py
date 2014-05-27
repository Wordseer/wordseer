"""Unit tests for the SparseVector module.
"""

import unittest

from app.wordseer.sparsevector import SparseVector

class SparseVectorTests(unittest.TestCase):
    """Test to make sure that SparseVector is functioning properly.
    """

    def test_add(self):
        """Test to make sure that addition is working properly.
        """

        vector1 = SparseVector({"foo": 3, "bar": 2})
        vector2 = SparseVector({"foo": 2, "baz": 3})
        expected_sum = SparseVector({"foo": 5, "bar": 2, "baz": 3})

        # Order of addition should not matter
        radd = vector1 + vector2
        ladd = vector2 + vector1

        assert radd == ladd
        assert radd == expected_sum

    def test_dot_prodcut(self):
        """Test to make sure that multiplication of two vectors is a dot
        product.
        """

        vector1 = SparseVector({"foo": 3, "bar": 2})
        vector2 = SparseVector({"foo": 2, "baz": 3})
        expected_product = 6

        # Order of operations should not matter
        rmul = vector1 * vector2
        lmul = vector2 * vector1

        assert rmul == lmul
        assert rmul == expected_product

    def test_scalar_multiply(self):
        """Test to make sure that scalar multiplication works.
        """

        vector1 = SparseVector({"foo": 3, "bar": 2})
        scalar = 4

        expected_product = SparseVector({"foo": 12, "bar": 8})

        # Order of operations shouldn't matter
        rmul = scalar * vector1
        lmul = scalar * vector1

        assert rmul == lmul
        assert rmul == expected_product

    def test_normalize(self):
        """Test normalization of vectors.
        """

        vector1 = SparseVector({"foo": 3, "bar": 2})
        expected_vector = SparseVector({"foo": .6, "bar": .4})

        assert vector1.normalize() == expected_vector
        assert expected_vector == expected_vector.normalize()

