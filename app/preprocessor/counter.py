"""This module serves to separate the process of filling in count fields for
models.
"""

from app import db
from app.models import Document, Dependency, Sequence, Word
import logging

def count(project):
    """Count ``sentence_count`` and ``document_count`` for ``Document``\s,
    ``Dependency``\s, and ``Sequence``\s.

    Arguments:
        project (Project): The project to do counts for.
    """

    logger = logging.getLogger(__name__)

    count = 0
    total_count = 0
    commit_interval = 500

    # Calculate counts for documents
    for document in project.get_documents():
        document.sentence_count = len(document.all_sentences)
        document.save(False)

        if count >= commit_interval:
            db.session.commit()
            count = 0
            logger.info('Counted %s documents.' % total_count)
        else:
            count += 1
            total_count += 1

    db.session.commit()
    logger.info('Counted %s documents.' % total_count)

    count = 0
    total_count = 0

    # Calculate counts for dependencies
    count_query = db.session.execute("""
        SELECT dependency_id,
            COUNT(DISTINCT document_id) AS document_count,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM dependency_in_sentence
        GROUP BY dependency_id
    """)

    for row in count_query.fetchall():
        dependency = Dependency.query.get(row.dependency_id)
        dependency_counts = dependency.get_counts(project)

        dependency_counts.document_count = row.document_count
        dependency_counts.sentence_count = row.sentence_count

        dependency_counts.save(False)
        dependency.save(False)

        if count >= commit_interval:
            db.session.commit()
            count = 0
            logger.info('Counted %s dependencies.' % total_count)
        else:
            count += 1
            total_count += 1

    db.session.commit()
    logger.info('Counted %s dependencies.' % total_count)

    count = 0
    total_count = 0

    # Calculate counts for sequences
    count_query = db.session.execute("""
        SELECT sequence_id,
            COUNT(DISTINCT document_id) AS document_count,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM sequence_in_sentence
        GROUP BY sequence_id
    """)

    for row in count_query.fetchall():
        sequence = Sequence.query.get(row.sequence_id)
        sequence_counts = sequence.get_counts(project)

        sequence_counts.document_count = row.document_count
        sequence_counts.sentence_count = row.sentence_count

        sequence_counts.save(False)
        sequence.save(False)

        if count >= commit_interval:
            db.session.commit()
            count = 0
            logger.info('Counted %s sequences.' % total_count)
        else:
            count += 1
            total_count += 1

    db.session.commit()
    logger.info('Counted %s sequences.' % total_count)

    count = 0
    total_count = 0

    # Calculate counts for words
    count_query = db.session.execute("""
        SELECT word_id,
            COUNT(DISTINCT sentence_id) AS sentence_count
        FROM word_in_sentence
        GROUP BY word_id
    """)

    for row in count_query.fetchall():
        word = Word.query.get(row.word_id)
        word_counts = word.get_counts(project)

        word_counts.sentence_count = row.sentence_count

        word_counts.save(False)
        word.save(False)

        if count >= commit_interval:
            db.session.commit()
            count = 0
            logger.info('Counted %s words.' % total_count)
        else:
            count += 1
            total_count += 1

    db.session.commit()
    logger.info('Counted %s words.' % total_count)

    count = 0
    total_count = 0
