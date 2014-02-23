from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
documents = Table('documents', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_id', Integer),
    Column('title', String),
    Column('source', String),
)

metadatas = Table('metadatas', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_id', Integer),
    Column('property_name', String),
    Column('property_value', String),
)

sentences = Table('sentences', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_id', Integer),
    Column('text', Text),
)

units = Table('units', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('unit_type', String(length=64)),
    Column('number', Integer),
)

word_in_sentence = Table('word_in_sentence', post_meta,
    Column('word_id', Integer),
    Column('sentence_id', Integer),
)

words = Table('words', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('word', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['documents'].create()
    post_meta.tables['metadatas'].create()
    post_meta.tables['sentences'].create()
    post_meta.tables['units'].create()
    post_meta.tables['word_in_sentence'].create()
    post_meta.tables['words'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['documents'].drop()
    post_meta.tables['metadatas'].drop()
    post_meta.tables['sentences'].drop()
    post_meta.tables['units'].drop()
    post_meta.tables['word_in_sentence'].drop()
    post_meta.tables['words'].drop()
