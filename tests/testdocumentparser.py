"""
Tests for the DocumentParser.
"""

import unittest
from mock import MagicMock, patch

from document.sentence import Sentence
from sequence.sequenceprocessor import SequenceProcessor
import logger
from parser import documentparser

class DocumentParserTests(unittest.TestCase):
    """Run tests on the DocumentParser.
    """
    def setUp(self):
        """Get the documentparser instance.
        """
        self.mock_reader_writer = MagicMock()
        self.mock_parser = MagicMock()
        self.docparser = documentparser.DocumentParser(self.mock_reader_writer,
            self.mock_parser)

    @patch.object(SequenceProcessor, "process", autospec=True)
    @patch.object(logger, "log", autospec=True)
    def test_write_and_parse(self, mock_logger, mock_seqproc):
        """Test the write_and_parse method.

        This method patches logger.log
        (to make sure that things are logged properly) as well as
        SequenceProcessor. It mocks DataReaderWriter.
        """
        
        sentences = [Sentence(text="This is the first sentence"),
            Sentence(text="This is the second sentence")]
        current_max = 5
        products = "products"

        # Configure the readerwriter mock
        attrs = {"write_parse_products.return_value": sentences}
        self.mock_reader_writer.configure_mock(**attrs)

        self.docparser.write_and_parse(products, current_max)

        # write_parse_products should have been called with the products arg
        self.mock_reader_writer.write_parse_products.\
            assert_called_once_with(products)

        # Logger should have been called twice with specific arguments
        mock_logger.assert_any_call(documentparser.LATEST_SENT_ID,
            str(current_max),
            logger.REPLACE)
