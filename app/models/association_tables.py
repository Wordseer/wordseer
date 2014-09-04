"""Simple many-to-many associations that don't require additional data.
"""
from app import db

sentences_in_sentencesets = db.Table("sentences_in_sentencesets",
    db.metadata,
    db.Column("sentence_id", db.Integer, db.ForeignKey("sentence.id")),
    db.Column("sentenceset_id", db.Integer, db.ForeignKey("sentence_set.id"))
)

documents_in_documentsets = db.Table("documents_in_documentsets",
    db.metadata,
    db.Column("document_id", db.Integer, db.ForeignKey("document.id")),
    db.Column("documentset_id", db.Integer, db.ForeignKey("document_set.id"))
)

bigrams_in_bigramsets = db.Table("bigrams_in_bigramsets",
    db.metadata,
    db.Column("bigram_id", db.Integer, db.ForeignKey("bigram.id")),
    db.Column("bigram_set_id", db.Integer, db.ForeignKey("bigram_set.id")),
)

document_files_in_projects = db.Table("document_files_in_projects",
    db.metadata,
    db.Column("document_file_id", db.Integer, db.ForeignKey("document_file.id")),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"))
)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

bigrams_in_sentences = db.Table("bigrams_in_sentences",
        db.Column("bigram_offset_id", db.Integer, db.ForeignKey("bigram_offset.id")),
        db.Column("sentence_id", db.Integer, db.ForeignKey("sentence.id"))
)

