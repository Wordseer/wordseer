import argparse
import config
import database
import logger # TODO: logger is different now
import os
from structureextractor import StructureExtractor
import tokenizer

class CollectionProcessor(object):
    def process(self, collection_dir, document_structure_file_name,
        file_name_extension, dbname, username, password, start_from_scratch):
        """
        This function:
        1. Sets up the database if necessary
        2. Extracts metadata, populates the narratives, sentenes, and paragraphs
        tables
        3. Processes the sentences by tokenizing and indexing the words
        4. Processes the sentences by performing grammatical parsing
        Arguments:
        start_from_scratch: If true, then the tables in the database will be
        recreated.
        """
        # Set up database if necessary
        if start_from_scratch is True:
            with database.Database() as db:
                db.reset()

        # TODO: MySQLDataReaderWriter

        t = tokenizer.Tokenizer()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        if not "true" in logger.get("finished_recording_text_and_metadata"):
            print("Extracting document text and metadata")
            extractor = StructureExtractor(t, document_structure_file_name)

            # Extract and record metadata, text for documents in the collection
            num_files_done = 1
            if os.path.isdir(collection_dir):
                contents = []
                for filename in os.listdir(collection_dir):
                    if (os.path.splitext(filename)[1].lower() ==
                        file_name_extension.lower()):
                        contents.append(filename)

                docs = [] # list of Documents

                for filename in contents:
                    if (not "[" + num_files_done + "]" in
                        logger.get("text_and_metadata_recorded") and
                        not filename[0] == "."):
                        logger.log("finished_recording_text_and_metadata",
                            "false", "replace")
                        try:
                            docs = extractor.extract(filename)
                            for doc in docs:
                                # TODO: readerwriter
                                pass
                            print("\t" + num_files_done + "/" +
                                str(len(contents)) + "\t" + filename)
                            logger.log("text_and_metadata_recorded",
                                num_files_done + "", "update")
                        except Exception as e:
                            print("Error on file " + filename)
                            print(e)

                    num_files_done += 1

                logger.log("finished_recording_text_and_metadata", "true",
                    "replace")
            else:
                raise IOError("Directory not found: " + collection_dir)

        # Parse the documents
        if config.GRAMMATICAL_PROCESSING or (config.WORD_TO_WORD_SIMILARITY and
            config.PART_OF_SPEECH_TAGGING):
            print("Parsing documents")
            # Initialize the parser

    def main(self, argv): #TODO: make this better

        """
        options.addOption("r", "reset", false, "Clear database and restart processing");
		options.addOption("d", "data", true, "The path to your XML data files");
		options.addOption("s", "structure", true, "The path to the JSON file explaining the structure of the XML files");
		options.addOption("i", "instance", true, "The short (20-characters or fewer) label to use for this WordSeer instance.");

		options.addOption("h", "help", false, "Print this message");
        """
        argparser = argparse.ArgumentParser(description="")
        argparser.add_argument("-r", action="store_true", dest="reset",
            help="Clear database and restart processing")
        argparser.add_argument("-d", action="store", dest="data",
            help="The path to your XML data files", required=True)
        argparser.add_argument("-s", action="store", dest="structure",
            help=("The path to the JSON file explaining the structure of the"
            " xml files"), required=True)
        argparser.add_argument("-i", action="store", dest="instance",
            help=("The short (20-characters or fewer) label to use for this"
            " WordSeer instance."), required=True)

        args = vars(argparser.parse(argv))

        db_name = "ws_" + args["instance"]
        self.process(args["data"], args["structure"], "xml", db_name,
            "wordseer", "wordseer", args["reset"])
