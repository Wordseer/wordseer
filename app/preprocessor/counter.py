from app import db
from app.models import Document, Dependency

"""This module serves to separate the process of filling in count fields for
models.
"""

def count():

	# Calculate counts for documents
    for document in Document.query.all():
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
            # for sequence in sentence.sequences:
            #     sequence.sentence_count = len(sequence.sentences)
            #     sequence.document_count = len(set([sentence.document
            #         for sentence in sequence.sentences]))
            #     sequence.save(False)

    db.session.commit()
