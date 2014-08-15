"""This module serves to separate the process of filling in count fields for
models.
"""

import logging

from app import db
from app.models import Document, Dependency, Sequence
from .logger import ProjectLogger
from app.models import Document, Dependency, Sequence, Word

def count(project):
    """Count ``sentence_count`` and ``document_count`` for ``Document``\s,
    ``Dependency``\s, and ``Sequence``\s.

    Arguments:
        project (Project): The project to do counts for.
    """

    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)

    count = 0
    commit_interval = 500

    # Calculate counts for documents
    documents = project.get_documents()

    project_logger.info("Calculating counts for documents")

    for document in documents:
        document.sentence_count = len(document.all_sentences)
        document.save(False)
        count += 1

        if count >= commit_interval:
            db.session.commit()
            project_logger.info("Calculating count for document %s/%s", count,
                len(documents))

    db.session.commit()
    project_logger.info('Counted %s documents.', len(documents))

    # Calculate counts for dependencies
    dependencies_in_sentences = db.session.execute("""
        SELECT dependency_id,
            COUNT(DISTINCT document_id) AS document_count,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM dependency_in_sentence
        GROUP BY dependency_id
    """).fetchall()

    project_logger.info("Calculating counts for dependencies")
    count = 0

    for row in dependencies_in_sentences:
        count += 1

        dependency = Dependency.query.get(row.dependency_id)
        dependency_counts = dependency.get_counts(project)

        dependency_counts.document_count = row.document_count
        dependency_counts.sentence_count = row.sentence_count

        dependency_counts.save(False)
        dependency.save(False)

        if count % commit_interval == 0:
            db.session.commit()
            logger.info('Counted %s dependencies.' % total_count)
            project_logger.info("Calculating count for dependency %s/%s", count,
                len(dependencies_in_sentences))

    db.session.commit()
    count = 0
    project_logger.info('Counted %s dependencies.',
        len(dependencies_in_sentences))

    # Calculate counts for sequences
    sequences_in_sentences = db.session.execute("""
        SELECT sequence_id,
            COUNT(DISTINCT document_id) AS document_count,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM sequence_in_sentence
        GROUP BY sequence_id
    """).fetchall()

    project_logger.info("Calculating counts for sequences")

    for row in sequences_in_sentences:
        count += 1

        sequence = Sequence.query.get(row.sequence_id)
        sequence_counts = sequence.get_counts(project)

        sequence_counts.document_count = row.document_count
        sequence_counts.sentence_count = row.sentence_count

        sequence_counts.save(False)
        sequence.save(False)

        if count >= commit_interval:
            db.session.commit()
            project_logger.info("Calculating count for sequence %s/%s", count,
                len(sequences_in_sentences))

    db.session.commit()
    project_logger.info('Counted %s sequences.',
        len(sequences_in_sentences))

    count = 0

    # Calculate counts for words
    words_in_sentences = db.session.execute("""
        SELECT word_id,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM word_in_sentence
        GROUP BY word_id
    """).fetchall()

    for row in words_in_sentences:
        count += 1
        word = Word.query.get(row.word_id)
        word_counts = word.get_counts(project)

        word_counts.sentence_count = row.sentence_count

        word_counts.save(False)
        word.save(False)

        if count >= commit_interval:
            db.session.commit()
            project_logger.info("Calculating count for word %s/%s", count,
                len(words_in_sentences))

    db.session.commit()
    project_logger.info('Counted %s words.',
        len(words_in_sentences))

