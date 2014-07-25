"""Tests for the DocumentParser.
"""
import unittest
from mock import MagicMock, patch, call, create_autospec
import pdb

from app.models.document import Document
from app.models.sentence import Sentence
from app.models.parsedparagraph import ParsedParagraph
from app.pipeline.parser import documentparser
from app.pipeline.stringprocessor import StringProcessor

@patch("app.pipeline.parser.documentparser.logger", autospec=True)
class DocumentParserTests(unittest.TestCase):
    """Run tests on the DocumentParser.
    """
    def setUp(self):
        """Get the documentparser instance.
        """
        self.mock_reader_writer = MagicMock()
        self.mock_str_proc = MagicMock()
        with patch("app.pipeline.parser.documentparser.SequenceProcessor"):
            self.docparser = documentparser.DocumentParser(
                self.mock_reader_writer,
                self.mock_str_proc)

    @patch("app.pipeline.parser.documentparser.db", autospec=True)
    def test_parse_document(self, mock_db, mock_logger):
        """Test the parse_document method.

        This method supplies a document of sixty sentences to make sure that
        everything works properly, and mocks out everything except for
        parse_document().
        """
        latest_sent = 5
        runs = 108
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
            parse_calls.append(call(mock_sents[i].text, {}, {}))
        self.mock_str_proc.parse.assert_has_calls(parse_calls, any_order=True)

        # Every 50 sentences we commit to the database
        assert len(mock_db.session.commit.call_args_list) == (runs - latest_sent + 1) / 50 + 1

