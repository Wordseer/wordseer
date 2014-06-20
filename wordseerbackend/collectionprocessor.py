"""
This file has tools to process a collection of files. This is the interface
between the input and the pipeline.
"""

from datetime import datetime
import os

from . import config
from .database.database import Database
from . import logger
from .parser.documentparser import DocumentParser
from .sequence.sequenceprocessor import SequenceProcessor
from . import structureextractor
from .stringprocessor import StringProcessor

class CollectionProcessor(object):
    """Process a collection of files.
    """
    def __init__(self, reader_writer):
        self.reader_writer = reader_writer
        self.str_proc = StringProcessor()

    def process(self, collection_dir, docstruc_filename,
        filename_extension, start_from_scratch):
        """
        This function relies on several methods to:

        1. Set up the database if necessary
        2. Extract metadata, populate the narratives, sentences, and paragraphs
            tables
        3. Process the sentences by tokenizing and indexing the words
        4. Process the sentences by performing grammatical parsing

        :param str collection_dir: The directory whose files should be
            processed.
        :param str docstructure_file_name: The name of the JSON file that
            describes the structure in the document files.
        :param str file_name_extension: Files with this extension will be parsed
            as documents.
        :param boolean start_from_scratch: If true, then the tables in the
            database will be recreated.
        """
        # Set up database if necessary
        if start_from_scratch is True:
            with Database() as database:
                database.reset()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        if not "true" in logger.get("finished_recording_text_and_metadata"):
            print("Extracting document text and metadata")
            self.extract_record_metadata(collection_dir,
                docstruc_filename, filename_extension)

        # Parse the documents
        if ((config.GRAMMATICAL_PROCESSING or
            (config.WORD_TO_WORD_SIMILARITY and
            config.PART_OF_SPEECH_TAGGING)) and not
            "true" in logger.get("finished_grammatical_processing").lower()):
            print("Parsing documents")
            self.parse_documents()

        if (config.SEQUENCE_INDEXING and
            "true" in logger.get("finished_sequence_processing").lower()):
            print "finishing indexing sequences"
            self.calculate_index_sequences()
            #TODO: reader_writer
            self.reader_writer.finish_indexing_sequences()

        # Calculate word-in-sentence counts and TF-IDFs
        if not "true" in logger.get("word_counts_done").lower():
            print("Calculating word counts")
            #TODO: reader_writer
            self.reader_writer.calculate_word_counts()
            logger.log("word_counts_done", "true", logger.REPLACE)

        # Calculate word TFIDFs
        if not "true" in logger.get("tfidf_done").lower():
            print("Calculating TF IDF's")
            #TODO: reader_writer
            self.reader_writer.calculate_tfidfs()

        # Calculate word-to-word-similarities
        if (config.WORD_TO_WORD_SIMILARITY and not
            "true" in logger.get("word_similarity_calculations_done")):
            print("Calculating Lin Similarities")
            #TODO: reader_writer
            self.reader_writer.calculate_lin_similarities()

    def extract_record_metadata(self, collection_dir, docstruc_filename,
        filename_extension):
        """Extract metadata from each file in collection_dir, and populate the
        documents, sentences, and document structure database tables.

        For every document file in ``collection_dir``, this extracts any
        documents from it using the
        :class:`~wordseerbackend.structureextractor.StructureExtractor`
        and the provided ``docstruc_filename``.

        Then, every document extracted is recorded with
        ``create_new_document`` from the reader/writer. Once all documents
        have been extracted, ``finished_recording_text_and_metadata`` is set to
        ``true`` using the :mod:`~wordseerbackend.logger`.

        :param StringProcessor str_proc: An instance of StringProcessor
        :param str collection_dir: The directory from which files should be
            parsed.
        :param str docstruc_file_name: A JSON description of the
            document structure.
        :param str filename_extension: The extension of the files that contain
            documents.
        """
        extractor = structureextractor.StructureExtractor(self.str_proc,
            docstruc_filename)

        # Extract and record metadata, text for documents in the collection
        num_files_done = 1
        contents = []
        for filename in os.listdir(collection_dir):
            if (os.path.splitext(filename)[1].lower() ==
                filename_extension.lower()):
                contents.append(filename)

        docs = [] # list of Documents

        for filename in contents:
            if (not "[" + str(num_files_done) + "]" in
                logger.get("text_and_metadata_recorded") and not
                filename[0] == "."):
                logger.log("finished_recording_text_and_metadata", "false",
                    logger.REPLACE)
                docs = extractor.extract(os.path.join(collection_dir,
                    filename))
                for doc in docs:
                    # TODO: readerwriter
                    self.reader_writer.create_new_document(doc,
                       num_files_done)

                print("\t" + str(num_files_done) + "/" + str(len(contents))
                    + "\t" + filename)
                logger.log("text_and_metadata_recorded",
                    str(num_files_done), logger.UPDATE)


            num_files_done += 1

        logger.log("finished_recording_text_and_metadata", "true",
            logger.REPLACE)

    def parse_documents(self):
        """Parse documents in the database using
        :meth:`~wordseerbackend.parser.documentparser.DocumentParser.parse_document`.

        Given the documents already loaded into the database from
        :meth:`~wordseerbackend.collectionprocessor.CollectionProcessor.extract_record_metadata`,
        parse each document using
        :meth:`~wordseerbackend.parser.documentparser.DocumentParser.parse_document`.
        Afterwards, call ``finish_grammatical_processing`` on the reader/writer.
        """

        # TODO: readerwriter
        document_ids = self.reader_writer.list_document_ids()
        document_parser = DocumentParser(self.reader_writer, self.str_proc)
        documents_parsed = 0
        latest = logger.get("latest_parsed_document_id")

        if len(latest) == 0:
            latest = "0"

        latest_id = int(latest)

        for doc_id in document_ids:
            if doc_id > latest_id:
                #TODO: readerwriter
                doc = self.reader_writer.get_document(doc_id)
                print("Parsing document " + str(documents_parsed) + "/" +
                    str(len(document_ids)))
                start_time = datetime.now()
                document_parser.parse_document(doc)
                seconds_elapsed = (datetime.now() - start_time).total_seconds()
                print("\tTime to parse document: " + str(seconds_elapsed) +
                    "s\n")
                logger.log("finished_grammatical_processing", "false",
                    logger.REPLACE)
                logger.log("latest_parsed_document_id", str(doc_id),
                    logger.REPLACE)

            documents_parsed += 1

        #TODO: reader_writer
        self.reader_writer.finish_grammatical_processing()

    def calculate_index_sequences(self):
        """Calculate and index sequences, if not already done during grammatical
        processing.

        For every sentence logged in the database with an ID less than the
        ID returned by ``get_max_setnece_id``, this method retrieves it and
        calls
        :meth:`~wordseerbackend.sequenceprocessor.SequenceProcessor.process`
        on it.
        """

        latest_sentence = logger.get("latest_sequence_sentence")

        if len(latest_sentence) == 0:
            latest_sentence = "0"

        latest_id = int(latest_sentence)
        # TODO: readerwriter
        max_sentence_id = self.reader_writer.get_max_sentence_id()
        sentences_processed = 0
        seq_proc = SequenceProcessor(self.reader_writer)
        #TODO: readerwriter
        self.reader_writer.load_sequence_counts()
        for i in range(latest_id, max_sentence_id):
            if i > latest_id:
                #TODO: readerwriter
                sentence = self.reader_writer.get_sentence(i)
                if len(sentence.words) > 0:
                    latest_id = sentence.id
                    processed_sequences = seq_proc.process(sentence)
                    if processed_sequences:
                        logger.log("finished_sequence_processing", "false",
                            logger.REPLACE)
                        logger.log("latest_sequence_sentence", str(i),
                            logger.REPLACE)
                if sentences_processed % 1000 == 0:
                    print("Sequence-processing sentence " + str(i) + "/" +
                        str(max_sentence_id))

            sentences_processed += 1
