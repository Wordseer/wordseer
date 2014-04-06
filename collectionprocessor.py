"""
This file has tools to process a collection of files and contains the command
line interface to the wordseer backend.
"""

import argparse
from datetime import datetime
import os
import sys

import config
from database.database import Database
import logger
from parser.documentparser import DocumentParser
from sequence.sequenceprocessor import SequenceProcessor
from structureextractor import StructureExtractor
from stringprocessor import StringProcessor

#TODO: probably better to move the arguments to instance variables

class CollectionProcessor(object):
    """Process a collection of files.
    """
    def __init__(self, reader_writer):
        self.reader_writer = reader_writer
        self.str_proc = StringProcessor()

    def process(self, collection_dir, docstruc_filename,
        filename_extension, start_from_scratch):
        """
        This function relies on several subfunctions to:
        1. Sets up the database if necessary
        2. Extracts metadata, populates the narratives, sentenes, and paragraphs
        tables
        3. Processes the sentences by tokenizing and indexing the words
        4. Processes the sentences by performing grammatical parsing

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
        if (config.GRAMMATICAL_PROCESSING or (config.WORD_TO_WORD_SIMILARITY and
            config.PART_OF_SPEECH_TAGGING) and not
            "true" in logger.get("finished_grammatical_processing").lower()):
            print("Parsing documents")
            self.parse_documents()

        if (config.SEQUENCE_INDEXING and
            "true" in logger.get("finished_sequence_processing").lower()):
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

        :param StringProcessor str_proc: An instance of StringProcessor
        :param str collection_dir: The directory from which files should be
        parsed.
        :param str docstruc_file_name: A JSON description of the
        document structure.
        :param str filename_extension: The extension of the files that contain
        documents.
        """
        extractor = StructureExtractor(self.str_proc, docstruc_filename)

        # Extract and record metadata, text for documents in the collection
        num_files_done = 1
        contents = []
        for filename in os.listdir(collection_dir):
            if (os.path.splitext(filename)[1].lower() ==
                filename_extension.lower()):
                contents.append(filename)

        docs = [] # list of Documents

        for filename in contents:
            if (not "[" + num_files_done + "]" in
                logger.get("text_and_metadata_recorded") and not
                filename[0] == "."):
                logger.log("finished_recording_text_and_metadata", "false",
                    logger.REPLACE)
                try:
                    docs = extractor.extract(filename)
                    for doc in docs:
                        # TODO: readerwriter
                        self.reader_writer.create_new_document(doc,
                           num_files_done)
                        pass

                    print("\t" + num_files_done + "/" + str(len(contents)) +
                        "\t" + filename)
                    logger.log("text_and_metadata_recorded",
                        num_files_done + "", logger.UPDATE)

                except Exception as e:
                    print("Error on file " + filename)
                    print(e)

            num_files_done += 1

        logger.log("finished_recording_text_and_metadata", "true",
            "replace")

    def parse_documents(self):
        """Given the documents already loaded into the database from
        extract_record_metadata, parse each document using
        DocumentParser.parse_document(). Afterwards, call
        ReaderWriter.finish_grammatical_processing.
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
                doc = self.reader_writer.get_document(id)
                print("Parsing document " + documents_parsed + "/" +
                    len(document_ids))
                start_time = datetime.now()
                document_parser.parse_document(doc)
                seconds_elapsed = (datetime.now() - start_time).total_seconds()
                print("\tTime to parse document: " + seconds_elapsed +
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

        For every sentence in the database, this method calls
        SequenceProcessor.process() on it.
        """

        latest_sentence = logger.get("latest_sequence_sentence")

        if len(latest_sentence) == 0:
            latest_sentence = "0"

        latest_id = int(latest_sentence)
        # TODO: readerwriter
        max_sentence_id = self.reader_writer.get_max_sentence_id
        sentences_processed = 0
        seq_proc = SequenceProcessor(self.reader_writer)
        #TODO: readerwriter
        self.reader_writer.load_sequence_counts()
        for i in range(latest_id, max_sentence_id):
            if i > latest_id:
                #TODO: readerwriter
                sentence = self.reader_writer.get_sentence(id)
                if len(sentence.words) > 0:
                    latest_id = sentence.id
                    processed_ok = seq_proc.process(sentence)
                    if processed_ok:
                        logger.log("finished_sequence_processing", "false",
                            logger.REPLACE)
                        logger.log("latest_sequence_sentence", str(i),
                            logger.REPLACE)
                if sentences_processed % 1000 == 0:
                    #TODO: is garbage collection necessary here?
                    print("Sequence-processing sentence " + i + "/" +
                        max_sentence_id)

            sentences_processed += 1

def main(argv):
    """This is the root method of the pipeline, this is where the user
    begins execution. It's meant to be run from the command line, given certain
    flags.

    :param list argv: The flags, usually received from the command line.
    """

    argparser = argparse.ArgumentParser(description="")
    argparser.add_argument("-r", action="store_true", dest="reset",
        help="Clear database and restart processing")
    argparser.add_argument("-d", action="store", dest="data",
        help="The path to your XML data files", required=True)
    argparser.add_argument("-s", action="store", dest="structure",
        help=("The path to the JSON file explaining the structure of the"
        " xml files"), required=True)

    args = vars(argparser.parse_args(argv))

    # TODO: MySQLDataReaderWriter
    #reader_writer = MySQLDataReaderWriter((config.GRAMMATICAL_PROCESSING or
    #   config.WORD_TO_WORD_SIMILARITY))
    #processor = CollectionProcessor(reader_writer)

    processor = CollectionProcessor("")
    processor.process(args["data"], args["structure"], "xml", args["reset"])

if __name__ == "__main__":
    main(sys.argv[1:])
