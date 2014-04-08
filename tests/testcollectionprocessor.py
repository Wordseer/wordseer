"""
Unit tests for the collectionprocessor module.
"""

import mock
import os
import unittest

import collectionprocessor
import config
from document.document import Document
import structureextractor
import logger
import stringprocessor

def setUpModule():
    global mock_writer
    mock_writer = mock.MagicMock(name="Mock Reader Writer")
    with mock.patch("collectionprocessor.StringProcessor",
        autospec=stringprocessor.StringProcessor):
        global colproc
        colproc = collectionprocessor.CollectionProcessor(mock_writer)

@mock.patch("collectionprocessor.logger", autospec=logger)
class TestCollectionProcessor(unittest.TestCase):
    """Test the CollectionProcessor class.
    """
    @mock.patch("collectionprocessor.StringProcessor",
        autospec=stringprocessor.StringProcessor)
    @mock.patch("collectionprocessor.StructureExtractor",
        autospec=structureextractor.StructureExtractor)
    @mock.patch("collectionprocessor.os", autospec=os)
    def test_extract_record_metadata(self, mock_os, mock_strucex, mock_str_proc,
        mock_logger):
        """Test the extract_record_metadata method.
        """
        # Set up the input objects
        collection_dir = mock.create_autospec(str)
        docstruc_filename = mock.create_autospec(str)
        filename_extension = ".xml"
        files = ["file1.xml", "file2.XmL", "file3.foo", ".file4.xml"]

        mock_os.listdir.return_value = files
        mock_os.path.splitext.side_effect = os.path.splitext

        mock_logger.get.return_value = ""

        # Make the structure extractor return useful objects
        extracted_docs = [mock.create_autospec(Document) for x in range(10)]
        mock_strucex.extract.return_value = extracted_docs
        
        colproc.extract_record_metadata(collection_dir, docstruc_filename,
            filename_extension)

        # logger.log() should have been called twice for each file like this
        log_calls = []
        for i in range(0, 2):
            log_calls.append(mock.call("finished_recording_text_and_metadata",
                "false", mock_logger.REPLACE))
            log_calls.append(mock.call("text_and_metadata_recorded", str(i + 1),
                mock_logger.UPDATE))
        mock_logger.log.assert_has_calls(log_calls)

        # The extractor should have been called on each file
        strucex_calls = [mock.call(files[0]), mock.call(files[1])]
        for call in strucex_calls:
            print mock_strucex.extract
            self.failUnless(call in mock_strucex.extract.call_args_list)

        # The reader writer should be called on every extracted doc
        createdoc_calls = [mock.call(doc) for doc in extracted_docs]
        mock_writer.create_new_document.assert_has_calls(createdoc_calls)

    @mock.patch("collectionprocessor.StringProcessor",
        autospec=stringprocessor.StringProcessor)
    def test_parse_documents(self, mock_str_proc, mock_logger):
        pass

    def test_calculate_index_sequences(self, mock_logger):
        pass

class TestCollectionProcessorProcess(unittest.TestCase):
    """Tests specifically for CollectionProcessor.process().
    """
    def setUp(self):
        colproc.calculate_index_sequences = mock.create_autospec(
            colproc.calculate_index_sequences)
            #name="calc_index_sequences",)
        colproc.parse_documents = mock.create_autospec(
            colproc.parse_documents)
            #name="parse_documents",)
        colproc.extract_record_metadata = mock.create_autospec(
            colproc.extract_record_metadata)
            #name="extract_record_metadata",)

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

        # Reset the previously used mocks
        mock_writer.reset_mock()

    @mock.patch("collectionprocessor.Database")
    def test_process_reset(self, mock_db):
        """Test that database reset works properly.
        """
        colproc.process("", "", "", True)

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
        colproc.process(*self.args)

        assert colproc.extract_record_metadata.called
        assert colproc.calculate_index_sequences.called == False
        assert colproc.parse_documents.called == False
        assert len(colproc.reader_writer.method_calls) == 0

    @mock.patch("collectionprocessor.config", autospec=config)
    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_parse_documents(self, mock_logger, mock_config):
        """Test that parse_documents is called properly
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        # Should only run parse_documents
        self.log_dict["finished_grammatical_processing"] = "false"
        mock_config.SEQUENCE_INDEXING = False
        colproc.process(*self.args)

        assert colproc.parse_documents.call_count == 1
        assert colproc.calculate_index_sequences.called == False
        assert colproc.extract_record_metadata.called == False
        assert len(colproc.reader_writer.method_calls) == 0

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_calc_index_sequences(self, mock_logger):
        """Test that calculate_index_sequences() is called along with
        the reader_writer.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        # Should run calculate_index_sequences() and run the reader_writer
        colproc.process(*self.args)

        assert colproc.calculate_index_sequences.call_count == 1
        assert mock_writer.finish_indexing_sequences.call_count == 1
        assert len(mock_writer.method_calls) == 1
        assert colproc.parse_documents.called == False
        assert colproc.extract_record_metadata.called == False

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_calc_word_counts(self, mock_logger):
        """Test that ReaderWriter.calculate_word_counts() is called along with
        the logs being updated.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        self.log_dict["word_counts_done"] = "false"
        self.log_dict["finished_sequence_processing"] = "false"
        colproc.process(*self.args)

        assert mock_writer.calculate_word_counts.call_count == 1
        assert len(mock_writer.method_calls) == 1
        assert colproc.calculate_index_sequences.called == False
        assert colproc.parse_documents.called == False
        assert colproc.extract_record_metadata.called == False
        mock_logger.log.assert_called_once_with("word_counts_done", "true",
            mock_logger.REPLACE)

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_tfidfs(self, mock_logger):
        """Test that ReaderWriter.calculate_tfidfs() is called.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__

        self.log_dict["tfidf_done"] = "false"
        self.log_dict["finished_sequence_processing"] = "false"
        colproc.process(*self.args)

        assert mock_writer.calculate_tfidfs.call_count == 1
        assert len(mock_writer.method_calls) == 1
        assert colproc.calculate_index_sequences.called == False
        assert colproc.parse_documents.called == False
        assert colproc.extract_record_metadata.called == False

    @mock.patch("collectionprocessor.logger", autospec=logger)
    def test_process_tfidfs(self, mock_logger):
        """Test that calculate_lin_similarities() is run.
        """
        mock_logger.get.side_effect = self.log_dict.__getitem__
        
        self.log_dict["word_similarity_calculations_done"] = "false"
        self.log_dict["finished_sequence_processing"] = "false"
        colproc.process(*self.args)

        assert mock_writer.calculate_lin_similarities.call_count == 1
        assert len(mock_writer.method_calls) == 1
        assert colproc.calculate_index_sequences.called == False
        assert colproc.parse_documents.called == False
        assert colproc.extract_record_metadata.called == False
