"""
Unit tests for the collectionprocessor module.
"""

import mock
import unittest

import collectionprocessor
import config
import logger
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

    @mock.patch("collectionprocessor.logger", autospec=logger)
    @mock.patch("collectionprocessor.StringProcessor",
        autospec=stringprocessor.StringProcessor)
    def test_extract_record_metadata(self, mock_str_proc, mock_logger):
        pass

    @mock.patch("collectionprocessor.logger", autospec=logger)
    @mock.patch("collectionprocessor.StringProcessor",
        autospec=stringprocessor.StringProcessor)
    def test_parse_documents(self, mock_str_proc, mock_logger):
        pass

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_calculate_index_sequences(self, mock_logger):
        pass

class TestCollectionProcessorProcess(TestCollectionProcessor):
    """Tests specifically for CollectionProcessor.process().
    """
    def setUp(self):
        super(TestCollectionProcessorProcess, self).setUp()
        self.colproc.calculate_index_sequences = mock.MagicMock(
            name="calc_index_sequences",
            autospec=self.colproc.calculate_index_sequences)
        self.colproc.parse_documents = mock.MagicMock(
            name="parse_documents",
            autospec=self.colproc.parse_documents)
        self.colproc.extract_record_metadata = mock.MagicMock(
            name="extract_record_metadata",
            autospec=self.colproc.extract_record_metadata)

    @mock.patch("collectionprocessor.Database")
    def test_process_reset(self, mock_db):
        """Test that database reset works properly.
        """
        self.colproc.process("", "", "", True)

        mock_db.reset.assert_called_once()

    @mock.patch("collectionprocessor.config", autospec=config)
    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_config(self, mock_logger, mock_config):
        """Mock the config module and test all possible config values.
        """
        args = ["", "", "", False]

        mock_logger.get.return_value = "true"
        self.colproc.process(*args)
        
        self.colproc.extract_record_metadata.assert_called_once()

class TestMain(unittest.TestCase):
    """Test the main() method in collectionprocessor.
    """

    @mock.patch("collectionprocessor.CollectionProcessor",
        autospec=collectionprocessor.CollectionProcessor)
    def test_main(self, mock_col_proc):
        collectionprocessor.main("-d test -s test".split(" "))
