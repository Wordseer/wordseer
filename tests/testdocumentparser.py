"""Tests for the DocumentParser.
"""
import unittest
from mock import MagicMock, patch, call, create_autospec

from app.models.document import Document
from app.models.sentence import Sentence
from app.models.parsedparagraph import ParsedParagraph
from lib.wordseerbackend.wordseerbackend.parser import documentparser
from lib.wordseerbackend.wordseerbackend.stringprocessor import StringProcessor

@patch("lib.wordseerbackend.wordseerbackend.parser.documentparser.logger",
    autospec=True)
class DocumentParserTests(unittest.TestCase):
    """Run tests on the DocumentParser.
    """
    def setUp(self):
        """Get the documentparser instance.
        """
        self.mock_reader_writer = MagicMock()
        self.mock_str_proc = MagicMock()
        with patch("lib.wordseerbackend.wordseerbackend.parser.documentparser.SequenceProcessor"):
            self.docparser = documentparser.DocumentParser(
                self.mock_reader_writer,
                self.mock_str_proc)

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

    def test_parse_document(self, mock_logger):
        """Test the parse_document method.

        This method supplies a document of sixty sentences to make sure that
        everything works properly, and mocks out everything except for
        parse_document().
        """
        latest_sent = 5
        runs = 60
        # Mock out the write_and_parse method
        self.docparser.write_and_parse = MagicMock()

        # Simulate a logger
        attrs = {"get.return_value": str(latest_sent)}
        mock_logger.configure_mock(**attrs)

        # Simulate a document with lots of sentences
        mock_sents = []
        for i in range(0, runs):
            mock_sents.append(MagicMock(id=i, name="Sentence " + str(i)))

        mock_doc = create_autospec(Document, sentences=mock_sents)

        # Configure the mock parser
        mock_products = MagicMock(name="Mock products")
        attrs = {"parse.return_value": mock_products}
        self.mock_str_proc.configure_mock(**attrs)

        # Run the method
        self.docparser.parse_document(mock_doc)

        # Nothing should have been logged
        self.failIf(mock_logger.log.called)

        # The parser should have only been called on sentences with an id > 5
        parse_calls = []
        for i in range(latest_sent + 1, runs):
            parse_calls.append(call(mock_sents[i].text))
        self.mock_str_proc.parse.assert_has_calls(parse_calls, any_order=True)

        # Write and parse should have been called once for every block of 50
        parsed = ParsedParagraph()
        rw_calls = []
        max_id = 0
        for i in range(latest_sent + 1, runs):
            parsed.add_sentence(mock_sents[i], mock_products)
            max_id = i
            if len(parsed.sentences) % 50 == 0:
                rw_calls.append(call(parsed, i))
                parsed = ParsedParagraph()

        rw_calls.append(call(parsed, max_id))

        self.docparser.write_and_parse.assert_has_calls(rw_calls,
            any_order=True)

