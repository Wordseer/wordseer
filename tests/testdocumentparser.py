"""
Tests for the DocumentParser.
"""

import unittest
from mock import MagicMock, patch, call

from document.sentence import Sentence
from document.parsedparagraph import ParsedParagraph
from parser import documentparser

@patch("parser.documentparser.logger")
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
        self.docparser.sequence_processor = MagicMock()


    def test_write_and_parse(self, mock_logger):
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
        mock_logger.log.assert_any_call(documentparser.LATEST_SENT_ID,
            str(current_max),
            mock_logger.REPLACE)
        mock_logger.log.assert_any_call(documentparser.LATEST_SEQ_SENT,
            str(current_max),
            mock_logger.REPLACE)

        # The sequence processor should have been invoked for every sentence
        self.docparser.sequence_processor.process.assert_any_call(sentences[0])
        self.docparser.sequence_processor.process.assert_any_call(sentences[1])

        self.mock_reader_writer.write_sequences.assert_called_once_with()

    def test_parse_document_long(self, mock_logger):
        """Test the parse_document method.

        This method supplies a document of sixty sentences to make sure that
        everything works properly, and mocks out everything except for
        parse_document().
        """
        # Mock out the write_and_parse method
        self.docparser.write_and_parse = MagicMock()

        # Simulate a logger
        attrs = {"get.return_value": "5"}
        mock_logger.configure_mock(**attrs)

        # Simulate a document with lots of sentences
        mock_sents = []
        for i in range(0, 60):
            mock_sents.append(MagicMock(id=i, name="Sentence " + str(i)))

        mock_doc = MagicMock(sentences=mock_sents)

        # Configure the mock parser
        mock_products = MagicMock(name="Mock products")
        attrs = {"parse.return_value": mock_products}
        self.mock_parser.configure_mock(**attrs)

        # Run the method
        self.docparser.parse_document(mock_doc)

        # Nothing should have been logged
        self.failIf(mock_logger.log.called)

        # The parser should have only been called on sentences with an id > 5
        parse_calls = []
        for i in range(6, 60):
            parse_calls.append(call(mock_sents[i].sentence))
        self.mock_parser.parse.assert_has_calls(parse_calls, any_order=True)

        # Write and parse should have been called once for every block of 50
        rw_calls = []
        parsed = ParsedParagraph()
        for i in range(6, 56):
            parsed.add_sentence(mock_sents[i], mock_products)

        rw_calls.append(call(parsed, 55))
        parsed = ParsedParagraph()

        for i in range(56, 60):
            parsed.add_sentence(mock_sents[i], mock_products)

        rw_calls.append(call(parsed, 59))
        self.docparser.write_and_parse.assert_has_calls(rw_calls,
            any_order=True)
