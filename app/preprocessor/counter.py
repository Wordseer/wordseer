"""This module serves to separate the process of filling in count fields for
models.
"""

import logging

from app import db
from app.models import Document, Dependency, Sequence
from .logger import ProjectLogger

def count(project):
    """Count ``sentence_count`` and ``document_count`` for ``Document``\s,
    ``Dependency``\s, and ``Sequence``\s.

    Arguments:
        project (Project): The project to do counts for.
    """
    # Calculate counts for documents
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)

    documents = project.get_documents()

    project_logger.info("Calculating counts for documents")
    count = 1
    for document in documents:
        project_logger.info("Calculating count for document %s/%s", count,
            len(documents))
        document.sentence_count = len(document.all_sentences)
        document.save(False)
        count += 1

    db.session.commit()

    # Calculate document counts for dependencies
    dependencies_in_sentences = db.session.execute("""
        SELECT dependency_id, COUNT(DISTINCT document_id) AS count
        FROM dependency_in_sentence
        GROUP BY dependency_id
    """).fetchall()

    project_logger.info("Calculating counts for dependencies")
    count = 1
    for row in dependencies_in_sentences:
        project_logger.info("Calculating count for dependency %s/%s", count,
            len(dependencies_in_sentences))
        dependency = Dependency.query.get(row.dependency_id)
        dependency.document_count = row.count

        dependency.save(False)
        count += 1

    db.session.commit()

    # Calculate document counts for sequences
    sequences_in_sentences = db.session.execute("""
        SELECT sequence_id, COUNT(DISTINCT document_id) AS count
        FROM sequence_in_sentence
        GROUP BY sequence_id
    """).fetchall()

    project_logger.info("Calculating counts for sequences")
    count = 1
    for row in sequences_in_sentences:
        project_logger.info("Calculating count for dependency %s/%s", count,
            len(sequences_in_sentences))
        sequence = Sequence.query.get(row.sequence_id)
        sequence.document_count = row.count

        sequence.save(False)
        count += 1

    db.session.commit()

