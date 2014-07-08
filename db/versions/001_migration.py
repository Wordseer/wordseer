from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
cached_sentences = Table('cached_sentences', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
)

dependency = Table('dependency', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('grammatical_relationship_id', Integer),
    Column('governor_id', Integer),
    Column('dependent_id', Integer),
    Column('sentence_count', Integer),
    Column('document_count', Integer),
)

dependency_in_sentence = Table('dependency_in_sentence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('dependency_id', Integer),
    Column('sentence_id', Integer),
    Column('governor_index', Integer),
    Column('dependent_index', Integer),
)

document = Table('document', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String),
    Column('path', String),
    Column('sentence_count', Integer),
)

document_set = Table('document_set', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
)

documents_in_documentsets = Table('documents_in_documentsets', post_meta,
    Column('document_id', Integer),
    Column('documentset_id', Integer),
)

documents_in_projects = Table('documents_in_projects', post_meta,
    Column('document_id', Integer),
    Column('project_id', Integer),
)

grammatical_relationship = Table('grammatical_relationship', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
)

project = Table('project', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String),
    Column('path', String),
    Column('user_id', Integer),
)

property = Table('property', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_id', Integer),
    Column('name', String),
    Column('value', String),
)

property_metadata = Table('property_metadata', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('type', String),
    Column('is_category', Boolean),
    Column('display_name', String),
    Column('display', Boolean),
)

role = Table('role', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=80)),
    Column('description', String(length=255)),
)

roles_users = Table('roles_users', post_meta,
    Column('user_id', Integer),
    Column('role_id', Integer),
)

sentence = Table('sentence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_id', Integer),
    Column('document_id', Integer),
    Column('text', Text),
)

sentence_set = Table('sentence_set', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
)

sentences_in_queries = Table('sentences_in_queries', post_meta,
    Column('sentence_id', Integer),
    Column('query_id', Integer),
)

sentences_in_sentencesets = Table('sentences_in_sentencesets', post_meta,
    Column('sentence_id', Integer),
    Column('sentenceset_id', Integer),
)

sequence = Table('sequence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('sequence', String),
    Column('lemmatized', Boolean),
    Column('has_function_words', Boolean),
    Column('all_function_words', Boolean),
    Column('length', Integer),
    Column('sentence_count', Integer),
    Column('document_count', Integer),
)

sequence_in_sentence = Table('sequence_in_sentence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('sequence_id', Integer),
    Column('sentence_id', Integer),
    Column('position', Integer),
)

sequence_set = Table('sequence_set', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
)

sequences_in_sequencesets = Table('sequences_in_sequencesets', post_meta,
    Column('sequence_id', Integer),
    Column('sequenceset_id', Integer),
)

set = Table('set', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('name', String),
    Column('creation_date', Date),
    Column('type', String),
)

unit = Table('unit', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_type', String(length=64)),
    Column('number', Integer),
    Column('parent_id', Integer),
    Column('path', String),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('email', String(length=255)),
    Column('password', String(length=255)),
    Column('active', Boolean),
    Column('confirmed_at', DateTime),
)

word = Table('word', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word', String),
    Column('lemma', String),
    Column('tag', String),
)

word_in_sentence = Table('word_in_sentence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word_id', Integer),
    Column('sentence_id', Integer),
    Column('position', Integer),
    Column('space_before', String),
    Column('tag', String),
)

word_in_sequence = Table('word_in_sequence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word_id', Integer),
    Column('sequence_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cached_sentences'].create()
    post_meta.tables['dependency'].create()
    post_meta.tables['dependency_in_sentence'].create()
    post_meta.tables['document'].create()
    post_meta.tables['document_set'].create()
    post_meta.tables['documents_in_documentsets'].create()
    post_meta.tables['documents_in_projects'].create()
    post_meta.tables['grammatical_relationship'].create()
    post_meta.tables['project'].create()
    post_meta.tables['property'].create()
    post_meta.tables['property_metadata'].create()
    post_meta.tables['role'].create()
    post_meta.tables['roles_users'].create()
    post_meta.tables['sentence'].create()
    post_meta.tables['sentence_set'].create()
    post_meta.tables['sentences_in_queries'].create()
    post_meta.tables['sentences_in_sentencesets'].create()
    post_meta.tables['sequence'].create()
    post_meta.tables['sequence_in_sentence'].create()
    post_meta.tables['sequence_set'].create()
    post_meta.tables['sequences_in_sequencesets'].create()
    post_meta.tables['set'].create()
    post_meta.tables['unit'].create()
    post_meta.tables['user'].create()
    post_meta.tables['word'].create()
    post_meta.tables['word_in_sentence'].create()
    post_meta.tables['word_in_sequence'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['cached_sentences'].drop()
    post_meta.tables['dependency'].drop()
    post_meta.tables['dependency_in_sentence'].drop()
    post_meta.tables['document'].drop()
    post_meta.tables['document_set'].drop()
    post_meta.tables['documents_in_documentsets'].drop()
    post_meta.tables['documents_in_projects'].drop()
    post_meta.tables['grammatical_relationship'].drop()
    post_meta.tables['project'].drop()
    post_meta.tables['property'].drop()
    post_meta.tables['property_metadata'].drop()
    post_meta.tables['role'].drop()
    post_meta.tables['roles_users'].drop()
    post_meta.tables['sentence'].drop()
    post_meta.tables['sentence_set'].drop()
    post_meta.tables['sentences_in_queries'].drop()
    post_meta.tables['sentences_in_sentencesets'].drop()
    post_meta.tables['sequence'].drop()
    post_meta.tables['sequence_in_sentence'].drop()
    post_meta.tables['sequence_set'].drop()
    post_meta.tables['sequences_in_sequencesets'].drop()
    post_meta.tables['set'].drop()
    post_meta.tables['unit'].drop()
    post_meta.tables['user'].drop()
    post_meta.tables['word'].drop()
    post_meta.tables['word_in_sentence'].drop()
    post_meta.tables['word_in_sequence'].drop()
