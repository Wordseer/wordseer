"""This module serves to separate the process of filling in count fields for
models.
"""

import logging
from sqlalchemy import func
from sqlalchemy.sql.expression import desc

from app import db
from app.models import *
from .logger import ProjectLogger

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
    count_sentences_by_property(project, commit_interval)

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

    dependency_counts = db.session.query(
        Dependency.id.label("dependency_id"),
        func.count(Sentence.document_id.distinct()).label("document_count"),
        func.count(DependencyInSentence.sentence_id).label("sentence_count")).\
    filter(DependencyInSentence.dependency_id == Dependency.id).\
    filter(DependencyInSentence.sentence_id == Sentence.id).\
    filter(Sentence.project_id == project.id).\
    group_by(Dependency.id)

    num_dependencies = db.session.query(Dependency.id).count()

    project_logger.info("Calculating counts for dependencies")

    for row in dependency_counts:
        count += 1
        dependency = Dependency.query.get(row.dependency_id)
        dep_count = DependencyCount(
            dependency=dependency,
            project=project,
            document_count=row.document_count,
            sentence_count=row.sentence_count)
        dep_count.save(False)
        dependency.save(False)
        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for dependency %s/%s", count,
                num_dependencies)
    db.session.commit()
    project_logger.info('Counted %s dependencies.', count)

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
    sequence_counts = db.session.query(
        Sequence.id.label("sequence_id"),
        func.count(Sentence.document_id.distinct()).label("document_count"),
        func.count(SequenceInSentence.sentence_id).label("sentence_count")).\
    filter(SequenceInSentence.sequence_id == Sequence.id).\
    filter(SequenceInSentence.sentence_id == Sentence.id).\
    filter(Sentence.project_id == project.id).\
    group_by(Sequence.id)

    num_sequences = db.session.query(Sequence.id).count()

    project_logger.info("Calculating counts for sequences")

    for row in sequence_counts:
        count += 1
        sequence = Sequence.query.get(row.sequence_id)
        sequence_count = SequenceCount(
            project=project,
            sequence=sequence,
            document_count=row.document_count,
            sentence_count=row.sentence_count)
        sequence_count.save(False)
        sequence.save(False)

        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for sequence %s/%s", count,
                num_sequences)

    db.session.commit()
    project_logger.info('Counted %s sequences.', count)

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

    num_words = db.session.query(Word.id).count()
    word_counts = db.session.query(
        Word.id.label("word_id"),
        func.count(Sentence.document_id.distinct()).label("document_count"),
        func.count(WordInSentence.sentence_id).label("sentence_count")).\
    filter(WordInSentence.word_id == Word.id).\
    filter(WordInSentence.sentence_id == Sentence.id).\
    filter(Sentence.project_id == project.id).\
    group_by(Word.id)

    for row in word_counts:
        count += 1
        word = Word.query.get(row.word_id)
        word_count = WordCount(
            project=project,
            word=word,
            document_count=row.document_count,
            sentence_count=row.sentence_count)
        word_count.save(False)
        word.save(False)
        if count % commit_interval == 0:
            db.session.commit()
            project_logger.info("Calculating count for word %s/%s", count,
                num_words)

    db.session.commit()
    project_logger.info('Counted %s words.', count)

def count_sentences_by_property(project, commit_interval):
    """Calculate counts for sentences matching properties.

    Arguments:
        project (Project): The ``Project`` to run counts for.
        commit_interval (int): This method will commit the counts every this
            many times.
    """
    count = 0
    logger = logging.getLogger(__name__)
    project_logger = ProjectLogger(logger, project)

    # get master list of properties
    properties = db.session.query(
        PropertyMetadata.property_name.label("name"),
        PropertyMetadata.data_type.label("data_type"),
        PropertyMetadata.date_format.label("date_format"),
        PropertyMetadata.id.label("id")
    ).\
    join(Property, Property.property_metadata_id == PropertyMetadata.id).\
    filter(Property.project_id == project.id).\
    filter(~PropertyMetadata.property_name.contains('_set')).\
    filter(PropertyMetadata.is_category == True).\
    group_by(PropertyMetadata.property_name)

    count = 0
    for property in properties: 
        values = db.session.query(
            Property.value.label('value'),
            func.count(PropertyOfSentence.sentence_id).label("sentence_count")
        ).filter(Property.project_id == project.id).\
        filter(Property.name == property.name).\
        filter(PropertyOfSentence.property_id == Property.id).\
        order_by(desc("sentence_count")).\
        group_by(Property.value).\
        limit(20)

        property_obj = PropertyMetadata.query.get(property.id)

        for value in values:
            count += 1
            property_count = PropertyCount(
                project=project,
                property_metadata=property_obj,
                property_value=value.value,
                sentence_count=value.sentence_count
            )
            property_count.save(False)
            property_obj.save(False)
            if count % commit_interval == 0:
                db.session.commit()
                project_logger.info("Calculating sentence count for property/value pair %s", count)

    db.session.commit()
    project_logger.info('Counted %s property/value pairs.', count)
