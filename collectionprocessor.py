import database
import logger
import os
import tokenizer

class CollectionProcessor(object):
    def process(self, collection_dir, document_structure_file_name,
        file_name_extension, start_from_scratch):
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
            with db as database.Database()
                db.reset()
        logger = Logger()

        # TODO: MySQLDataReaderWriter?
        
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
                for file in os.listdir(collection_dir):
                    if file[-len(file_name_extension)].lower() ==
                        file_name_extension.lower():
                            contents.append(file)

                docs = [] # list of Documents

                for file in contents:
                    if not "[" + num_files_done + "]" in
                        logger.get("text_and_metadata_recorded") and
                        not file[0] == ".":
                            logger.log("finished_recording_text_and_metadata",
                                "false", "replace")
                            try:
                                docs = extractor.extract(file)
                                for doc in docs:
                                    # TODO: readerwriter
                                    pass
                                print("\t" + num_files_done + "/" + \
                                    len(contents) + "\t" + file)
                                logger.log("text_and_metadata_recorded",
                                    num_files_done + "", "update")
                            except e:
                                print("Error on file " + file)
                                print(e)
                                
                    ++num_files_done

                logger.log("finished_recording_text_and_metadata", "true",
                    "replace")
            else:
                raise IOError("Directory not found: " + collection_dir)

        # Parse the documents
        if config.GRAMMATICAL_PROCESSING or (config.WORD_TO_WORD_SIMILARITY and
            config.PART_OF_SPEECH_TAGGING):
                print("Parsing documents")
                # Initialize the parser
            
            
        