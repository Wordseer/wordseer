"""This module serves to separate the process of filling in count fields for
models.
"""

from app import db
from app.models import Document, Dependency

def count(project):
    """Count ``sentence_count`` and ``document_count`` for ``Document``\s,
    ``Dependency``\s, and ``Sequence``\s.

    Arguments:
        project (Project): The project to do counts for.
    """
    # Calculate counts for documents
    for document in project.documents:
        document.sentence_count = len(document.all_sentences)
        document.save(False)

        for sentence in document.all_sentences:
            # Calculate counts for dependencies
            for dependency in sentence.dependencies:
                dependency.sentence_count = len(dependency.sentences)
                dependency.document_count = len(set([sentence.document
                    for sentence in dependency.sentences]))
                dependency.save(False)

            # Calculate counts for sequences
            for sequence in sentence.sequences:
                sequence.sentence_count = len(sequence.sentences)
                sequence.document_count = len(set([sentence.document
                    for sentence in sequence.sentences]))
                sequence.save(False)
    db.session.commit()

