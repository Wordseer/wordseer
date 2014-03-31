"""
This file has tools to process a collection of files and contains the command
line interface to the wordseer backend.
"""

import argparse
import os
import sys

import config
from database import Database
import logger
from structureextractor import StructureExtractor
from stringprocessor import StringProcessor

#TODO: probably better to move the arguments to instance variables

class CollectionProcessor(object):
    """Process a collection of files.
    """
    def __init__(self, reader_writer):
        self.reader_writer = reader_writer
    
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

        # TODO: MySQLDataReaderWriter
        #reader_writer = MySQLDataReaderWriter(db, (grammatial_processing or
        #   word_to_word_similarity))

        str_proc = StringProcessor()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        if not "true" in logger.get("finished_recording_text_and_metadata"):
            print("Extracting document text and metadata")
            extract_record_metadata(str_proc, collection_dir,
                docstruc_filename, filename_extension)

        # Parse the documents
        if (config.GRAMMATICAL_PROCESSING or (config.WORD_TO_WORD_SIMILARITY and
            config.PART_OF_SPEECH_TAGGING) and not
            "true" in logger.get("finished_grammatical_processing").lower()):
            print("Parsing documents")
            parse_documents()

    def extract_record_metadata(str_proc, collection_dir, docstruc_filename,
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
        extractor = StructureExtractor(str_proc, docstruc_filename)

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
                        #self.reader_writer.create_new_document(doc,
                        #   num_files_done)
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

    def parse_documents():
        pass

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

    processor = CollectionProcessor()
    processor.process(args["data"], args["structure"], "xml", args["reset"])

if __name__ == "__main__":
    main(sys.argv[1:])
