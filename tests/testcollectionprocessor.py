"""
Unit tests for the collectionprocessor module.
"""

import mock
import unittest

import collectionprocessor
import stringprocessor

@mock.patch("collectionprocessor.StringProcessor")
class TestCollectionProcessor(unittest.TestCase):
    """Test the CollectionProcessor class.
    """
    def setUp(self):
        """Set up the CollectionProcessor and mock out dependencies.
        """
        self.mock_writer = mock.MagicMock(name="Mock Reader Writer")
        with mock.patch("collectionprocessor.StringProcessor",
            autospec=stringprocessor.StringProcessor):
            self.colproc = collectionprocessor.CollectionProcessor(
                self.mock_writer)
    
    def test_process(self, mock_str_proc):
        self.colproc.calculate_index_sequences = mock.create_autospec(
            self.colproc.calculate_index_sequences)
        self.colproc.parse_documents = mock.create_autospec(
            self.colproc.parse_documents)
        self.colproc.extract_record_metadata = mock.create_autospec(
            self.colproc.extract_record_metadata)
        print self.colproc.str_proc

    def test_extract_record_metadata(self, mock_str_proc):
        pass

    def test_parse_documents(self, mock_str_proc):
        pass

    def test_calculate_index_sequences(self, mock_str_proc):
        pass

class TestMain(unittest.TestCase):
    """Test the main() method in collectionprocessor.
    """

    @mock.patch("collectionprocessor.CollectionProcessor",
        autospec=collectionprocessor.CollectionProcessor)
    def test_main(self, mock_col_proc):
        collectionprocessor.main("-d test -s test".split(" "))
        