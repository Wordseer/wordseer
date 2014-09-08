"""This module serves to separate the process of filling in count fields for
models.
"""

import logging
from datetime import datetime

from app import app
from app import db
from .logger import ProjectLogger
from app.models import Document, Dependency, Word, Bigram, WordInSentence, Ngram
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
    count = 0
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)

    bigrams = Bigram.query.join(Word, Word.id==Bigram.word_id).\
        filter(Word.project_id == project.id).all()
    s1_bigrams = []
    s2_bigrams = []
    ngrams = []
    phrase_index = {}
    interesting_offsets = 0

    project_logger.info("Getting stage 1 bigrams")
    for bigram in bigrams:
        count += 1
        if bigram.get_strength() >= k0 and bigram.get_spread >= u0:
            # Promote these somehow
            offsets = bigram.pass_stage_one()
            interesting_offsets += offsets
            s1_bigrams.append(bigram)
        if count % commit_interval == 0:
            project_logger.info("Calculating count for bigram %s/%s", count,
                len(bigrams))
            db.session.commit()

    db.session.commit()
    project_logger.info("Got %s bigrams", count)
    project_logger.info("Counting %s ngrams with %s interesting offsets",
        len(s1_bigrams), interesting_offsets)
    count = 0
    t0 = datetime.now()

    for bigram in s1_bigrams:
        for bigram_offset in bigram.offsets:
            if bigram_offset.interesting:
                sentences = bigram_offset.sentences
                s22_bigrams = get_stage22_bigrams(sentences, bigram.word,
                    project)
                ngram = get_ngram(s22_bigrams, T)
                has_stops = has_stop_words(ngram)
                phrase = " ".join([word.lemma for word in ngram])
                if not all_stop_words(ngram):
                    if not phrase in phrase_index:
                        phrase_index[phrase] = Ngram(text=phrase,
                            has_stop_words=has_stops,
                            words=ngram)
                    phrase_index[phrase].count += len(bigram_offset.sentences)
        now = datetime.now()
        diff = (now - t0).total_seconds()
        project_logger.info("%s seconds to process bigram %s/%s", diff,
            count, len(s1_bigrams))
        t0 = now

        count += 1
        if count % commit_interval == 0:
            project_logger.info("Getting ngrams from bigram %s/%s", count,
                len(s1_bigrams))
            db.session.commit()

    db.session.commit()
    project_logger.info("Got %s ngrams", count)

def all_stop_words(words):
    text = [word.lemma for word in words]
    return all(word in app.config["STOPWORDS"] for word in text)


def has_stop_words(words):
    text = [word.lemma for word in words]
    return any(word in app.config["STOPWORDS"] for word in text)

def get_ngram(bigrams, T):
    wildcard = Word(lemma="WILDCARD")
    ngram = []
    frequencies = [0] * 10
    for bigram in bigrams:
        for i in range(0, 10):
            frequencies[i] += bigram.offsets[i].frequency

    #FIXME: misses last position
    for i in range(0, 10):
        word_to_add = wildcard

        if i == 5:
            ngram.append(bigram.word)
            continue

        for bigram in bigrams:
            if frequencies[i] > 0 and float(bigram.offsets[i].frequency) / frequencies[i] > T:
                word_to_add = bigram.secondary_word

        ngram.append(word_to_add)

    start_i = -1
    end_i = len(ngram)

    for i, x in enumerate(ngram):
        if x != wildcard:
            start_i = i
            break
    for i in range(len(ngram) - 1, -1, -1):
        if ngram[i] != wildcard:
            end_i = i
            break

    return ngram[start_i:end_i + 1]

def get_stage22_bigrams(sentences, word, project):
    """Execute stage 2.2 of xtract.
    """
    bigrams = {}

    for sentence in sentences:
       rel = WordInSentence.query.filter_by(sentence=sentence,
            word=word).first()

       start_index = max(rel.position - 5, 0)
       end_index = min(rel.position + 6, sentence.length)

       for i in range(start_index, end_index):
            if i - rel.position == 0:
                continue
            offset_rel = WordInSentence.query.filter_by(sentence=sentence,
                position=i).one()

            key = (word, offset_rel.word)

            if key in bigrams:
                bigram = bigrams[key]

            else:
                bigram = Bigram(word, offset_rel.word, project)
                bigram.stage = 22
                bigrams[key] = bigram

            bigram.add_instance(i - rel.position, sentence, False)

    return [bigram for key, bigram in bigrams.items()]

