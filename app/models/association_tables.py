"""Simple many-to-many associations that don't require additional data.
"""
from app import db

sentences_in_sentencesets = db.Table("sentences_in_sentencesets",
    db.metadata,
    db.Column("sentence_id", db.Integer, db.ForeignKey("sentence.id", ondelete='CASCADE')),
    db.Column("sentenceset_id", db.Integer, db.ForeignKey("sentence_set.id", ondelete='CASCADE'))
)

documents_in_documentsets = db.Table("documents_in_documentsets",
    db.metadata,
    db.Column("document_id", db.Integer, db.ForeignKey("document.id", ondelete='CASCADE')),
    db.Column("documentset_id", db.Integer, db.ForeignKey("document_set.id", ondelete='CASCADE'))
)

sequences_in_sequencesets = db.Table("sequences_in_sequencesets",
    db.metadata,
    db.Column("sequence_id", db.Integer, db.ForeignKey("sequence.id", ondelete='CASCADE')),
    db.Column("sequenceset_id", db.Integer, db.ForeignKey("sequence_set.id", ondelete='CASCADE')),
)

document_files_in_projects = db.Table("document_files_in_projects",
    db.metadata,
    db.Column("document_file_id", db.Integer, db.ForeignKey("document_file.id", ondelete='CASCADE')),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id", ondelete='CASCADE'))
)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
)