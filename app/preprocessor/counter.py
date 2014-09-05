"""This module serves to separate the process of filling in count fields for
models.
"""

import logging

from app import db
from .logger import ProjectLogger
from app.models import Document, Dependency, Word, Bigram
import pdb

def count_all(project, commit_interval=500):
    """Run counts for documents, dependencies, and words.

    Arguments:
        project (Project): The project to do counts for.
        commit_interval (int): How often to commit changes to the database.
    """
    count_documents(project, commit_interval)
    count_dependencies(project, commit_interval)
    count_words(project, commit_interval)
    count_bigrams(project, commit_interval)

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

def count_bigrams(project, commit_interval):
    """Run statistic analysis on bigrams.

    Arguments:
        project (Project): The ``Project`` to run counts for.
        commit_interval (int): This method will commit the counts every this
            many times.
    """
    k0 = 1 # Strength threshhold
    k1 = 1 # Distance threshhold
    u0 = 10 # Spread thresshold
    T = .5 # Probability threshhold

    bigrams = Bigram.query.join(Word, Word.id==Bigram.word_id).\
        filter(Word.project_id == project.id).all()
    s1_bigrams = []
    s2_bigrams = []
    ngrams = []

    for bigram in bigrams:
        if bigram.get_strength() >= k0 and bigram.get_spread >= u0:
            # Promote these somehow
            bigram.pass_stage_one()
            s1_bigrams.append(bigram)

    db.session.commit()

    for bigram in s1_bigrams:
        ngram = []
        for i in range(-5, 6):
            try:
                offset = bigram.get_offset(i)
            except ValueError:
                offset = 0

            if offset == 0:
                ngram.append(bigram.word)

            elif float(offset.frequency / bigram.frequency) > T:
                ngram.append(bigram.secondary_word)

            else:
                ngram.append("*")

        start_i = -1
        end_i = len(ngram)
        for i, x in enumerate(ngram):
            if x != "*":
                start_i = i
                break
        for i in range(len(ngram) - 1, -1, -1):
            if ngram[i] != "*":
                end_i = i
                break

        ngrams.append(ngram[start_i:end_i + 1])

    pdb.set_trace()

