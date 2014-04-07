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

        # Set up the dict that is our "logging database" and set the arguments
        # for calling process()
        self.log_dict = {"finished_recording_text_and_metadata": "true",
            "finished_grammatical_processing": "true",
            "finished_sequence_processing": "true",
            "word_counts_done": "true",
            "tfidf_done": "true",
            "word_similarity_calculations_done": "true"
        }
        
        self.args = ["", "", "", False]

    @mock.patch("collectionprocessor.Database")
    def test_process_reset(self, mock_db):
        """Test that database reset works properly.
        """
        self.colproc.process("", "", "", True)

        mock_db.reset.assert_called_once()

    @mock.patch("collectionprocessor.config", autospec=config)
    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_e_r_m(self, mock_logger, mock_config):
        """Test that extract_record_metadata() is called properly.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__
        # Should just extract_record_metadata
        self.log_dict["finished_recording_text_and_metadata"] = "false"
        mock_config.SEQUENCE_INDEXING = False
        mock_config.PART_OF_SPEECH_TAGGING = False
        mock_config.GRAMMATICAL_PROCESSING = False
        self.colproc.process(*self.args)

        assert self.colproc.extract_record_metadata.called
        assert self.colproc.calculate_index_sequences.called == False
        assert self.colproc.parse_documents.called == False
        assert len(self.colproc.reader_writer.method_calls) == 0

    @mock.patch("collectionprocessor.config", autospec=config)
    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_parse_documents(self, mock_logger, mock_config):
        """Test that parse_documents is called properly
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        # Should only run parse_documents
        self.log_dict["finished_grammatical_processing"] = "false"
        mock_config.SEQUENCE_INDEXING = False
        self.colproc.process(*self.args)

        assert self.colproc.parse_documents.call_count == 1
        assert self.colproc.calculate_index_sequences.called == False
        assert self.colproc.extract_record_metadata.called == False
        assert len(self.colproc.reader_writer.method_calls) == 0

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_calc_index_sequences(self, mock_logger):
        """Test that calculate_index_sequences() is called along with
        the reader_writer.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        # Should run calculate_index_sequences() and run the reader_writer
        self.colproc.process(*self.args)

        assert self.colproc.calculate_index_sequences.call_count == 1
        assert self.mock_writer.finish_indexing_sequences.call_count == 1
        assert len(self.mock_writer.method_calls) == 1
        assert self.colproc.parse_documents.called == False
        assert self.colproc.extract_record_metadata.called == False

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_calc_word_counts(self, mock_logger):
        """Test that ReaderWriter.calculate_word_counts() is called along with
        the logs being updated.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        self.log_dict["word_counts_done"] = "false"
        self.log_dict["finished_sequence_processing"] = "false"
        self.colproc.process(*self.args)

        assert self.mock_writer.calculate_word_counts.call_count == 1
        assert len(self.mock_writer.method_calls) == 1
        assert self.colproc.calculate_index_sequences.called == False
        assert self.colproc.parse_documents.called == False
        assert self.colproc.extract_record_metadata.called == False
        mock_logger.log.assert_called_once_with("word_counts_done", "true",
            mock_logger.REPLACE)

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_tfidfs(self, mock_logger):
        """Test that ReaderWriter.calculate_tfidfs() is called.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        self.log_dict["tfidf_done"] = "false"
        self.log_dict["finished_sequence_processing"] = "false"
        self.colproc.process(*self.args)

        assert self.mock_writer.calculate_tfidfs.call_count == 1
        assert len(self.mock_writer.method_calls) == 1
        assert self.colproc.calculate_index_sequences.called == False
        assert self.colproc.parse_documents.called == False
        assert self.colproc.extract_record_metadata.called == False

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_tfidfs(self, mock_logger):
        """Test that calculate_lin_similarities() is run.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__
        
        self.log_dict["word_similarity_calculations_done"] = "false"
        self.log_dict["finished_sequence_processing"] = "false"
        self.colproc.process(*self.args)

        assert self.mock_writer.calculate_lin_similarities.call_count == 1
        assert len(self.mock_writer.method_calls) == 1
        assert self.colproc.calculate_index_sequences.called == False
        assert self.colproc.parse_documents.called == False
        assert self.colproc.extract_record_metadata.called == False
        
class TestMain(unittest.TestCase):
    """Test the main() method in collectionprocessor.
    """

    @mock.patch("collectionprocessor.CollectionProcessor",
        autospec=collectionprocessor.CollectionProcessor)
    def test_main(self, mock_col_proc):
        collectionprocessor.main("-d test -s test".split(" "))
