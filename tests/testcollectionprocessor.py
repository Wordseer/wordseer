"""
Unit tests for the collectionprocessor module.
"""

import mock
import unittest

import collectionprocessor
import stringprocessor

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

    @mock.patch("collectionprocessor.StringProcessor")
    def test_extract_record_metadata(self, mock_str_proc):
        pass

    @mock.patch("collectionprocessor.StringProcessor")
    def test_parse_documents(self, mock_str_proc):
        pass

    @mock.patch("collectionprocessor.StringProcessor")
    def test_calculate_index_sequences(self, mock_str_proc):
        pass

class TestCollectionProcessorProcess(TestCollectionProcessor):
    """Tests specifically for CollectionProcessor.process().
    """
    def setUp(self):
        super(TestCollectionProcessorProcess, self).setUp()
        self.colproc.calculate_index_sequences = mock.create_autospec(
            self.colproc.calculate_index_sequences)
        self.colproc.parse_documents = mock.create_autospec(
            self.colproc.parse_documents)
        self.colproc.extract_record_metadata = mock.create_autospec(
            self.colproc.extract_record_metadata)
       
    @mock.patch("collectionprocessor.StringProcessor")
    def test_process_reset(self, mock_str_proc):
        """Test that database reset works properly.
        """
        pass

class TestMain(unittest.TestCase):
    """Test the main() method in collectionprocessor.
    """

    @mock.patch("collectionprocessor.CollectionProcessor",
        autospec=collectionprocessor.CollectionProcessor)
    def test_main(self, mock_col_proc):
        collectionprocessor.main("-d test -s test".split(" "))
        