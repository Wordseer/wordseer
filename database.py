# Modified from:
# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.schema import Index
from sys import argv

from app import app
from app import db
from app import models
from app import association_tables
from migrate.versioning import api
import imp

SQLALCHEMY_DATABASE_URI = app.config["SQLALCHEMY_DATABASE_URI"]
SQLALCHEMY_MIGRATE_REPO = app.config["SQLALCHEMY_MIGRATE_REPO"]

def create():
    create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO,
            api.version(SQLALCHEMY_MIGRATE_REPO))

def migrate():
    migration = (SQLALCHEMY_MIGRATE_REPO +
        '/versions/%03d_migration.py' % (api.db_version(SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_MIGRATE_REPO) + 1))
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_MIGRATE_REPO)
    #FIXME
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('New migration saved as ' + migration)
    print('Current database version: ' +
        str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def upgrade():
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('Current database version: ' +
        str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def downgrade():
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    print('Current database version: ' +
        str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def drop():
    os.remove(SQLALCHEMY_DATABASE_URI.split('///')[-1])
    shutil.rmtree(SQLALCHEMY_MIGRATE_REPO)

def reset():
    # Remove old database if it's there
    try:
        os.remove(SQLALCHEMY_DATABASE_URI.split('///')[-1])
    except OSError:
        print("Database not found; creating new database.")

    db.create_all()
    index()

def cache():
    """Copy the current database file to ``SQLALCHEMY_DATABASE_CACHE_PATH``.
    """
    shutil.copyfile(app.config["SQLALCHEMY_DATABASE_PATH"],
        app.config["SQLALCHEMY_DATABASE_CACHE_PATH"])

def restore_cache():
    """Copy the cached file to where the database file should be.
    """
    shutil.copyfile(app.config["SQLALCHEMY_DATABASE_CACHE_PATH"],
        app.config["SQLALCHEMY_DATABASE_PATH"])

def clean():
    """Restore cache and roll back the session.
    """
    restore_cache()
    db.session.rollback()
    db.session.expunge_all()

def index():
    """Create indexes because the ORM doesn't do it 
    TODO: is this because the db tables are being created by the preprocessor outside the ORM?
    What's the best way to update the preprocessor 
    """
    # drop all indexes (TODO: obviously this is not platform agnostic; SQLite3-specific)
    # NOTE: we are doing it this stupid way because SQLAlchemy doesn't have a
    # 'CREATE IF NOT EXISTS' equivalent for indexing, it just throws an error
    # result = db.engine.execute("SELECT name FROM sqlite_master WHERE type == 'index'")
    # indices = []
    # for row in result:
    #     if row[0].startswith("ix_"): #this is the naming convention we use
    #         indices.append(row[0])
    # for i in indices:
    #     db.session.execute("DROP INDEX " + i)
    # db.session.commit()
    #
    # print "all indices dropped"

    # create indices
    indices = [
        # single column indices
        Index('ix_count_sentcount', models.Count.sentence_count),
        Index('ix_count_doccount', models.Count.document_count),
        Index('ix_count_projid', models.Count.project_id),
        Index('ix_dependency_grammrelid', models.Dependency.grammatical_relationship_id),
        Index('ix_depinsent_depid', models.DependencyInSentence.dependency_id),
        Index('ix_depinsent_docid', models.DependencyInSentence.document_id),
        Index('ix_depinsent_projid', models.DependencyInSentence.project_id),
        Index('ix_document_docfileid', models.Document.document_file_id),
        Index('ix_document_title', models.Document.title),
        Index('ix_freqseq_projid', models.FrequentSequence.project_id),
        Index('ix_freqword_projid', models.FrequentWord.project_id),
        Index('ix_grammrel_name', models.GrammaticalRelationship.name),
        Index('ix_grammrel_projid', models.GrammaticalRelationship.project_id),
        Index('ix_log_item', models.Log.log_item),
        Index('ix_projectsusers_projid', models.ProjectsUsers.project_id),
        Index('ix_projectsusers_userid', models.ProjectsUsers.user_id),
        Index('ix_propmeta_pname', models.PropertyMetadata.property_name),
        Index('ix_propmeta_iscat', models.PropertyMetadata.is_category),
        Index('ix_propmeta_unittype', models.PropertyMetadata.unit_type),
        Index('ix_property_unitid', models.Property.unit_id),
        Index('ix_property_projid', models.Property.project_id),
        Index('ix_property_propmetaid', models.Property.property_metadata_id),
        Index('ix_property_name', models.Property.name),
        Index('ix_property_value', models.Property.value),
        Index('ix_propofsentence_propid', models.PropertyOfSentence.property_id),
        Index('ix_propofsentence_sentid', models.PropertyOfSentence.sentence_id),
        Index('ix_sentence_text', models.Sentence.text),
        Index('ix_sentence_projid', models.Sentence.project_id),
        Index('ix_sentence_docid', models.Sentence.document_id),
        Index('ix_sentenceinquery_sentid', models.SentenceInQuery.sentence_id),
        Index('ix_sentenceinquery_queryid', models.SentenceInQuery.query_id),
        Index('ix_sequence_sequence', models.Sequence.sequence),
        Index('ix_sequence_lemmatized', models.Sequence.lemmatized),
        Index('ix_sequence_hasfunc', models.Sequence.has_function_words),
        Index('ix_sequence_allfunc', models.Sequence.all_function_words),
        Index('ix_sequence_length', models.Sequence.length),
        Index('ix_sequence_projid', models.Sequence.project_id),
        Index('ix_seqcount_seqid', models.SequenceCount.sequence_id),
        Index('ix_seqinsentence_seqid', models.SequenceInSentence.sequence_id),
        Index('ix_seqinsentence_sentid', models.SequenceInSentence.sentence_id),
        Index('ix_seqinsentence_projid', models.SequenceInSentence.project_id),
        Index('ix_seqinsentence_docid', models.SequenceInSentence.document_id),
        Index('ix_seqinsentence_pos', models.SequenceInSentence.position),
        Index('ix_set_userid', models.Set.user_id),
        Index('ix_set_projid', models.Set.project_id),
        Index('ix_set_type', models.Set.type),
        Index('ix_strucfile_projid', models.StructureFile.project_id),
        Index('ix_unit_number', models.Unit.number),
        Index('ix_unit_projid', models.Unit.project_id),
        Index('ix_unit_parentid', models.Unit.parent_id),
        Index('ix_word_lemma', models.Word.lemma),
        Index('ix_word_pos', models.Word.part_of_speech),
        Index('ix_word_surface', models.Word.surface),
        Index('ix_wordinsentence_wordid', models.WordInSentence.word_id),
        Index('ix_wordinsentence_projid', models.WordInSentence.project_id),
        Index('ix_wordinsentence_pos', models.WordInSentence.position),
        Index('ix_wordinsequence_projid', models.WordInSequence.project_id),
        Index('ix_wordinsequence_seqid', models.WordInSequence.sequence_id),
        
        # TODO: it can't find this column in the table for some reason
        # Index('ix_wordcount_wordid', models.WordCount.word_id),

        # compound indices
        Index('ix_count_projid_id', models.Count.project_id, models.Count.id),
        Index('ix_docsindocsets_docid_docsetid', association_tables.documents_in_documentsets.c.document_id, association_tables.documents_in_documentsets.c.documentset_id),
        Index('ix_docfileinproj_docfileid_projid', association_tables.document_files_in_projects.c.document_file_id, association_tables.document_files_in_projects.c.project_id),
        Index('ix_docfileinproj_projid_docfileid', association_tables.document_files_in_projects.c.project_id, association_tables.document_files_in_projects.c.document_file_id),
        Index('ix_projectsusers_projid_userid', models.ProjectsUsers.project_id, models.ProjectsUsers.user_id),
        Index('ix_property_name_value', models.Property.name, models.Property.value),
        Index('ix_property_id_name_value', models.Property.id, models.Property.name, models.Property.value),
        Index("ix_property_projid_name_value", models.Property.project_id, models.Property.name, models.Property.value),
        Index('ix_property_projid_propmetaid', models.Property.project_id, models.Property.property_metadata_id),
        Index('ix_property_projid_name_value', models.Property.project_id, models.Property.name, models.Property.value),
        Index('ix_property_propmetaid_projid', models.Property.property_metadata_id, models.Property.project_id),
        Index("ix_propmeta_iscat_id",  models.PropertyMetadata.is_category, models.PropertyMetadata.id),
        Index('ix_propmeta_iscat_unittype', models.PropertyMetadata.is_category, models.PropertyMetadata.unit_type),
        Index("ix_propofsentence_sent_prop", models.PropertyOfSentence.sentence_id, models.PropertyOfSentence.property_id),
        Index("ix_sentence_projid_id", models.Sentence.project_id, models.Sentence.id),
        Index("ix_sentenceinquery_sentid_queryid", models.SentenceInQuery.sentence_id, models.SentenceInQuery.query_id),
        Index('ix_sequence_id_length', models.Sequence.length, models.Sequence.id),
        Index("ix_sequence_length_lemmatized", models.Sequence.length, models.Sequence.lemmatized),
        Index("ix_sequence_funcwords_length_id", models.Sequence.all_function_words, models.Sequence.length, models.Sequence.id),
        Index("ix_sequence_projid_id_lemmatized_sequence_length", models.Sequence.project_id, models.Sequence.id, models.Sequence.lemmatized, models.Sequence.sequence, models.Sequence.length),
        Index("ix_sequence_sequence_projid", models.Sequence.sequence, models.Sequence.project_id),
        Index('ix_sequencecount_projid_id', models.SequenceCount.sequence_id, models.SequenceCount.id),
        Index('ix_seqinsentence_seqid_sentid', models.SequenceInSentence.sequence_id, models.SequenceInSentence.sentence_id),
        Index('ix_seqinseqset_seqid_seqsetid', association_tables.sequences_in_sequencesets.c.sequence_id, association_tables.sequences_in_sequencesets.c.sequenceset_id),
        Index('ix_set_projid_parentid_type', models.Set.project_id, models.Set.parent_id, models.Set.type),
        Index('ix_set_projid_type', models.Set.project_id, models.Set.type),
        Index("ix_word_pos_id", models.Word.part_of_speech, models.Word.id),
        Index("ix_word_surface_lemma", models.Word.surface, models.Word.lemma),
        Index('ix_wordcount_wordid_id', models.WordCount.word_id, models.WordCount.id),
        Index('ix_wordinsent_wordid_sentid', models.WordInSentence.word_id, models.WordInSentence.sentence_id),
        # TODO: it can't find this column in the table for some reason
        # Index('ix_wordcount_projid_wordid', models.WordCount.project_id, models.WordCount.word_id),

    ]
    for i in indices:
        try:
            i.create(db.engine)
            print "created index:", i
        except OperationalError:
            print "index already exists:", i
    print "all indices created"


if __name__ == "__main__":

    if argv[1] == "create":
        create()
    elif argv[1] == "migrate":
        migrate()
    elif argv[1] == "upgrade":
        upgrade()
    elif argv[1] == "downgrade":
        downgrade()
    elif argv[1] == "drop":
        drop()
    elif argv[1] == "reset":
        reset()
    elif argv[1] == "index":
        index()
    else:
        print(str(argv[1]) + " is not a valid database operation.")
