"""This module serves to separate the process of filling in count fields for
models.
"""

from app import db
from app.models import Document, Dependency, Sequence

def count(project):
    """Count ``sentence_count`` and ``document_count`` for ``Document``\s,
    ``Dependency``\s, and ``Sequence``\s.

    Arguments:
        project (Project): The project to do counts for.
    """
    # Calculate counts for documents
    for document in project.get_documents():
        document.sentence_count = len(document.all_sentences)
        document.save(False)

    db.session.commit()

    # Calculate document counts for dependencies
    count_query = db.session.execute("""
        SELECT dependency_id, COUNT(DISTINCT document_id) AS count
        FROM dependency_in_sentence
        GROUP BY dependency_id
    """)

    for row in count_query.fetchall():
        dependency = Dependency.query.get(row.dependency_id)
        dependency.document_count = row.count

        dependency.save()

    db.session.commit()

    # Calculate document counts for sequences
    count_query = db.session.execute("""
        SELECT sequence_id, COUNT(DISTINCT document_id) AS count
        FROM sequence_in_sentence
        GROUP BY sequence_id
    """)

    for row in count_query.fetchall():
        sequence = Sequence.query.get(row.sequence_id)
        sequence.document_count = row.count

        sequence.save()

    db.session.commit()
