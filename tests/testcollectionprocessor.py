"""
Unit tests for the collectionprocessor module.
"""

import mock
import unittest

import collectionprocessor
import stringprocessor

@mock.patch("collectionprocessor.StringProcessor")
class TestCollectionProcessor(unittest.TestCase):
    @mock.patch("collectionprocessor.StringProcessor")
    def setUp(self, test):
        """Set up the CollectionProcessor and mock out dependencies.
        """
        self.mock_writer = mock.MagicMock(name="Mock Reader Writer")
        self.colproc = collectionprocessor.CollectionProcessor(self.mock_writer)
    
    def test_process(self, mock_str_proc):
        self.colproc.calculate_index_sequences = mock.create_autospec(
            self.colproc.calculate_index_sequences, False, False,
            name="Mock Calc Index Sequences")
        self.colproc.parse_documents = mock.create_autospec(
            self.colproc.parse_documents, name="Mock Parse")
        self.colproc.extract_record_metadata = mock.create_autospec(
            self.colproc.extract_record_metadata,
            name="Mock extract record metadata")
        print self.colproc.str_proc

    def test_extract_record_metadat(self, mock_str_proc):
        pass

