"""Unit tests for the collectionprocessor module.
"""

import mock
import os
import unittest

from app import app
from app.models.document import Document
from app.models.project import Project
from app.preprocessor import collectionprocessor
from app.preprocessor import stringprocessor
from app.preprocessor import structureextractor
from app.preprocessor import logger
from app.preprocessor import documentparser
from app.preprocessor import sequenceprocessor
import database

def setUpModule():
    global project
    project = Project()
    with mock.patch("app.preprocessor.collectionprocessor.StringProcessor",
            autospec=True):
        global colproc
        colproc = collectionprocessor.CollectionProcessor(project)

@mock.patch("app.preprocessor.collectionprocessor.logger", autospec=logger)
class TestCollectionProcessor(unittest.TestCase):
    """Test the CollectionProcessor class.
    """
    def setUp(self):
        database.clean()
        colproc.project = Project()

    @mock.patch("app.preprocessor.collectionprocessor.structureextractor",
        autospec=True)
    @mock.patch("app.preprocessor.collectionprocessor.os", autospec=True)
    def test_extract_record_metadata(self, mock_os, mock_strucex, mock_logger):
        """Test the extract_record_metadata method.
        """
        # Set up the input objects
        collection_dir = "/foobar/"
        docstruc_filename = mock.create_autospec(str)
        filename_extension = ".xml"
        files = ["file1.xml", "file2.XmL", "file3.foo", ".file4.xml"]

        # Configure the mock os
        mock_os.listdir.return_value = files
        mock_os.path.splitext.side_effect = os.path.splitext
        mock_os.path.join.side_effect = os.path.join

        # Configure mock logger
        mock_logger.get.return_value = ""

        # Make the structure extractor return useful objects
        extracted_docs = [
            (os.path.join(collection_dir, files[0]),
                [mock.create_autospec(Document) for x in range(10)]),
            (os.path.join(collection_dir, files[1]),
                [mock.create_autospec(Document) for x in range(10)])
        ]

        def extract_docs(filename):
            for entry in extracted_docs:
                if entry[0] == filename:
                    return entry[1]

        mock_strucex_instance = mock_strucex.StructureExtractor("", "")
        mock_strucex_instance.extract.side_effect = extract_docs

        # Run the SUT
        colproc.extract_record_metadata(collection_dir, docstruc_filename,
            filename_extension)

        # logger.log() should have been called twice for each file like this
        log_calls = []

        for i in range(0, 2):
            log_calls.append(mock.call(colproc.project,
                "finished_recording_text_and_metadata", "false",
                mock_logger.REPLACE))
            log_calls.append(mock.call(colproc.project,
                "text_and_metadata_recorded", str(i + 1), mock_logger.UPDATE))

        log_calls.append(mock.call(colproc.project,
            "finished_recording_text_and_metadata", "true",
            mock_logger.REPLACE))
        mock_logger.log.assert_has_calls(log_calls)

        # The extractor should have been called on each file
        strucex_calls = [mock.call(extracted_docs[0][0]),
            mock.call(extracted_docs[1][0])
        ]
        for call in strucex_calls:
            self.failUnless(call in mock_strucex_instance.extract.\
                call_args_list)

    @mock.patch("app.preprocessor.collectionprocessor.DocumentParser",
        autospec=True)
    @mock.patch("app.preprocessor.collectionprocessor.counter", autospec=True)
    def test_parse_documents(self, mock_counter, mock_dp, mock_logger):
        """Tests for the test_parse_documents method.
        """
        # Set up the mocks
        max_doc = 20
        mock_dp_instance = mock_dp.return_value

        colproc.project = mock.create_autospec(Project)

        mock_documents = [mock.create_autospec(Document, id=i)
            for i in range(max_doc)]

        colproc.project.get_documents.return_value = mock_documents

        latest = 5
        mock_logger.get.return_value = str(latest)

        # Run the SUT
        colproc.parse_documents()

        # Document parser should have been called on every doc
        parse_calls = [mock.call(mock_documents[i])
            for i in range(latest + 1, max_doc)]
        mock_dp_instance.parse_document.assert_has_calls(parse_calls)

        # Logger should be called twice per doc
        logger_calls = []
        for i in range(latest + 1, max_doc):
            logger_calls.append(mock.call(colproc.project,
                "finished_grammatical_processing", "false",
                mock_logger.REPLACE))
            logger_calls.append(mock.call(colproc.project,
                "latest_parsed_document_id", str(i), mock_logger.REPLACE))
        mock_logger.log.assert_has_calls(logger_calls)

        # Make sure the counter has been called
        mock_counter.count.assert_called_once_with(colproc.project)

class TestCollectionProcessorProcess(unittest.TestCase):
    """Tests specifically for CollectionProcessor.process().
    """
    def setUp(self):
        database.clean()
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
        # mock_writer.reset_mock()

    @mock.patch("app.preprocessor.collectionprocessor.logger", autospec=True)
    def test_process_e_r_m(self, mock_logger):
        """Test that extract_record_metadata() is called properly.
        """
        mock_logger.get.side_effect = lambda proj, query: self.log_dict[query]
        # Should just extract_record_metadata
        self.log_dict["finished_recording_text_and_metadata"] = "false"

        mock_config = {
            "SEQUENCE_INDEXING": False,
            "PART_OF_SPEECH_TAGGING": False,
            "GRAMMATICAL_PROCESSING": False,
        }

        with mock.patch.dict(app.config, mock_config):
            colproc.process(*self.args)

        assert colproc.extract_record_metadata.called
        assert colproc.parse_documents.called == False
        # assert len(colproc.reader_writer.method_calls) == 0

    @mock.patch("app.preprocessor.collectionprocessor.logger", autospec=True)
    def test_process_parse_documents(self, mock_logger):
        """Test that parse_documents is called properly
        """
        mock_logger.get.side_effect = lambda proj, query: self.log_dict[query]

        # Should only run parse_documents
        self.log_dict["finished_grammatical_processing"] = "false"

        mock_config = {
            "SEQUENCE_INDEXING": False
        }

        with mock.patch.dict(app.config, mock_config):
            colproc.process(*self.args)

        assert colproc.parse_documents.call_count == 1
        assert colproc.extract_record_metadata.called == False
        # assert len(colproc.reader_writer.method_calls) == 0

