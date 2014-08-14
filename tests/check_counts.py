from app.models import *
from app import db
from sqlalchemy import func, distinct

# Check sequence counts

for seqsent in SequenceInSentence.query.all():
    sequence = seqsent.sequence

    real_sentence_count = int(db.session.execute("""
        SELECT COUNT(*) AS count
        FROM sequence_in_sentence
        WHERE sequence_id = {0}
    """.format(sequence.id)).fetchone().count)

    if real_sentence_count != sequence.sentence_count:
        print("Mismatched sentence count for " + str(sequence))
        print('Calculated count: %s; real count: %s' % (sequence.sentence_count, real_sentence_count))

    real_document_count = int(db.session.execute("""
        SELECT COUNT(DISTINCT document_id) AS count
        FROM sequence_in_sentence
        WHERE sequence_id = {0}
    """.format(sequence.id)).fetchone().count)

    if real_document_count != sequence.document_count:
        print("Mismatched document count for " + str(sequence))
        print('Calculated count: %s; real count: %s' % (sequence.document_count, real_document_count))
        print("")
