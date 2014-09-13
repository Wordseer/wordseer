"""This module serves to separate the process of filling in count fields for
models.
"""

import logging

from app import db
from app.models import Document, Dependency, Sequence
from .logger import ProjectLogger
from app.models import Document, Dependency, Sequence, Word

def count_all(project, commit_interval=500):
    """Run counts for documents, dependencies, sequences, and words.

    Arguments:
        project (Project): The project to do counts for.
        commit_interval (int): How often to commit changes to the database.
    """
    count_documents(project, commit_interval)
    count_dependencies(project, commit_interval)
    count_sequences(project, commit_interval)
    count_words(project, commit_interval)

def count_documents(project, commit_interval):
    """Calculate counts for documents.

    Arguments:
        project (Project): The ``Project`` to run counts for.
        commit_interval (int): This method will commit the counts every this
            many times.
    """
    count = 0
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)
    documents = project.get_documents()

    project_logger.info("Calculating counts for documents")

    for document in documents:
        document.sentence_count = len(document.all_sentences)
        document.save(False)
        count += 1

        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for document %s/%s", count,
                len(documents))

    db.session.commit()
    project_logger.info('Counted %s documents.', len(documents))

def count_dependencies(project, commit_interval):
    """Calculate counts for dependencies.

    Arguments:
        project (Project): The ``Project`` to run counts for.
        commit_interval (int): This method will commit the counts every this
            many times.
    """
    count = 0
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)

    dependencies_in_sentences = db.session.execute("""
        SELECT dependency_id,
            COUNT(DISTINCT document_id) AS document_count,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM dependency_in_sentence
        WHERE project_id = %s
        GROUP BY dependency_id
    """ % project.id).fetchall()

    project_logger.info("Calculating counts for dependencies")

    for row in dependencies_in_sentences:
        dependency = Dependency.query.get(row.dependency_id)
        dependency_counts = dependency.get_counts(project)

        dependency_counts.document_count = row.document_count
        dependency_counts.sentence_count = row.sentence_count

        dependency_counts.save(False)
        dependency.save(False)

        count += 1
        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for dependency %s/%s", count,
                len(dependencies_in_sentences))

    db.session.commit()
    project_logger.info('Counted %s dependencies.',
        len(dependencies_in_sentences))

def count_sequences(project, commit_interval):
    """Calculate counts for sequences.

    Arguments:
        project (Project): The ``Project`` to run counts for.
        commit_interval (int): This method will commit the counts every this
            many times.
    """
    count = 0
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)
    #pdb.set_trace()
    sequences_in_sentences = db.session.execute("""
        SELECT sequence_id,
            COUNT(DISTINCT document_id) AS document_count,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM sequence_in_sentence
        WHERE project_id = %s
        GROUP BY sequence_id
    """ % project.id).fetchall()

    project_logger.info("Calculating counts for sequences")

    for row in sequences_in_sentences:
        count += 1

        sequence = Sequence.query.get(row.sequence_id)
        sequence_counts = sequence.get_counts(project)

        sequence_counts.document_count = row.document_count
        sequence_counts.sentence_count = row.sentence_count

        sequence_counts.save(False)
        sequence.save(False)

        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for sequence %s/%s", count,
                len(sequences_in_sentences))

    db.session.commit()
    project_logger.info('Counted %s sequences.',
        len(sequences_in_sentences))

def count_words(project, commit_interval):
    """Calculate counts for words.

    Arguments:
        project (Project): The ``Project`` to run counts for.
        commit_interval (int): This method will commit the counts every this
            many times.
    """
    count = 0
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)

    words_in_sentences = db.session.execute("""
        SELECT word_id,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM word_in_sentence
        WHERE project_id = %s
        GROUP BY word_id
    """ % project.id).fetchall()

    for row in words_in_sentences:
        count += 1
        word = Word.query.get(row.word_id)
        word_counts = word.get_counts(project)

        word_counts.sentence_count = row.sentence_count

        word_counts.save(False)
        word.save(False)

        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for word %s/%s", count,
                len(words_in_sentences))

    db.session.commit()
    project_logger.info('Counted %s words.',
        len(words_in_sentences))

