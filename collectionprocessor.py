import argparse
import config
import database
import logger
import os
from structureextractor import StructureExtractor
from stringprocessor import StringProcessor

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
        #reader_writer = MySQLDataReaderWriter(db, (grammatial_processing or
        #   word_to_word_similarity))

        str_proc = StringProcessor()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        if not "true" in logger.get("finished_recording_text_and_metadata"):
            print("Extracting document text and metadata")
            self.extract_record_metadata(str_proc,
                document_structure_file_name, collection_dir)

        # Parse the documents
        if config.GRAMMATICAL_PROCESSING or (config.WORD_TO_WORD_SIMILARITY and
            config.PART_OF_SPEECH_TAGGING):
            print("Parsing documents")
            if not "true" in logger.get("finished_grammatical_processing").lower()

    def extract_record_metadata(self, str_proc, document_structure_file_name,
        collection_dir):
        """Extract metadata from each file in collection_dir, and populate the
        documents, sentences, and document structure database tables.

        :param StringProcessor str_proc: An instance of StringProcessor
        :param str document_structure_file_name: A JSON description of the
        document structure.
        :param str collection_dir: The directory from which files should be
        parsed.
        """
        extractor = StructureExtractor(str_proc,
            document_structure_file_name)

        # Extract and record metadata, text for documents in the collection
        num_files_done = 1
        contents = []
        for filename in os.listdir(collection_dir):
            if (os.path.splitext(filename)[1].lower() ==
                file_name_extension.lower()):
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
                        #reader_writer.create_new_document(doc,
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
    argparser.add_argument("-i", action="store", dest="instance",
        help=("The short (20-characters or fewer) label to use for this"
        " WordSeer instance."), required=True)

    args = vars(argparser.parse(argv))

    db_name = "ws_" + args["instance"]
    self.process(args["data"], args["structure"], "xml", db_name,
        "wordseer", "wordseer", args["reset"])

if __name__ == "__main__":
    main(sys.argv[1:])
