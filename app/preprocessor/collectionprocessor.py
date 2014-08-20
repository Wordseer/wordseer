"""This file has tools to process a collection of files. This is the interface
between the input and the pipeline.
"""

from datetime import datetime
import logging
import os

from app import app
from app.models import Project
import database
from . import logger
from .documentparser import DocumentParser
from .sequenceprocessor import SequenceProcessor
from . import structureextractor
from .stringprocessor import StringProcessor
from . import counter
from app.models import Document, Base

class CollectionProcessor(object):
    """Process a collection of files.
    """
    def __init__(self, project):
        self.project = Project.query.get(project)
        self.str_proc = StringProcessor(self.project)
        self.pylogger = logging.getLogger(__name__)
        self.project_logger = logger.ProjectLogger(self.pylogger, self.project)

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

        Base.commit_on_save = False

	# Set up database if necessary
        if start_from_scratch is True:
            database.reset()

        self.project.status = Project.STATUS_PREPROCESSING
        self.project.save()

        # Extract metadata, populate documents, sentences, and doc structure
        # tables
        if not "true" in logger.get(self.project,
                "finished_recording_text_and_metadata"):
            self.project_logger.info("Extracting document text and metadata")
            self.extract_record_metadata(collection_dir,
                docstruc_filename, filename_extension)

        # Parse the documents
        if ((app.config["GRAMMATICAL_PROCESSING"] or
                (app.config["WORD_TO_WORD_SIMILARITY"] and
                app.config["PART_OF_SPEECH_TAGGING"])) and not
                "true" in logger.get(self.project,
                    "finished_grammatical_processing").lower()):
            self.project_logger.info("Parsing documents")
            self.parse_documents()

        # Calculate word-in-sentence counts and TF-IDFs
        if not "true" in logger.get(self.project, "word_counts_done").lower():
            self.project_logger.info("Calculating word counts")
            # TODO: implement a method to do word counts for sentences
            logger.log(self.project, "word_counts_done", "true", logger.REPLACE)

        # Calculate word TFIDFs
        if not "true" in logger.get(self.project, "tfidf_done").lower():
            self.project_logger.info("Calculating TF IDF's")
            # TODO: implement tfidf method in document

        # Calculate word-to-word-similarities
        if (app.config["WORD_TO_WORD_SIMILARITY"] and not
                "true" in logger.get(self.project,
                    "word_similarity_calculations_done")):
            self.project_logger.info("Calculating Lin Similarities")
            # TODO: implement similarities

        self.project_logger.info("Finished preprocessing.")
        self.project.status = Project.STATUS_DONE
        self.project.save()

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
                logger.get(self.project, "text_and_metadata_recorded") and not
                filename[0] == "."):
                logger.log(self.project, "finished_recording_text_and_metadata",
                    "false", logger.REPLACE)

                start_time = datetime.now()
                docs = extractor.extract(os.path.join(collection_dir,
                    filename))
                seconds_elapsed = (datetime.now() - start_time).total_seconds()

                self.project_logger.info("Finished extracting and recording "
                    "metadata for %s. Time: %ss (%s/%s).", filename,
                    seconds_elapsed, str(num_files_done), str(len(contents)))

                logger.log(self.project, "text_and_metadata_recorded",
                    str(num_files_done), logger.UPDATE)

            num_files_done += 1

        logger.log(self.project, "finished_recording_text_and_metadata", "true",
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

        documents = self.project.get_documents()
        document_parser = DocumentParser(self.str_proc, self.project)
        documents_parsed = 0
        latest = logger.get(self.project, "latest_parsed_document_id")

        if not latest:
            latest = "0"

        latest_id = int(latest)

        for document in documents:
            if document.id > latest_id:
                self.project_logger.info("Parsing document %s/%s (#%s)",
                    str(documents_parsed + 1), str(len(documents)),
                    str(document.id))

                start_time = datetime.now()
                document_parser.parse_document(document)
                seconds_elapsed = (datetime.now() - start_time).total_seconds()

                self.project_logger.info("Time to parse document: %ss",
                    str(seconds_elapsed))
                logger.log(self.project, "finished_grammatical_processing",
                    "false", logger.REPLACE)
                logger.log(self.project, "latest_parsed_document_id",
                    str(document.id), logger.REPLACE)

            else:
                self.project_logger.info("Skipping document %s/%s (#%s)",
                    str(documents_parsed + 1), str(len(documents)),
                    str(document.id))

            documents_parsed += 1

        counter.count(self.project)

def cp_run(collection_dir, structure_file, extension, project):
    """Run the collection processor.

    Arguments:
        collection_dir (str): Where to get files from.
        structure_file (str): The path to the structure file.
        extension (str): Extension of the document files.
        project (Project): Which project to use for this processing.
    """
    if extension[0] != ".":
        extension = "." + extension

    collection_processor = CollectionProcessor(project)
    collection_processor.process(collection_dir, structure_file, extension,
       False)

