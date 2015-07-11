"""Storage for precomputed lists of most frequent words and sequences in a project
"""
from app import app, db
from base import Base

class FrequentWord(db.Model, Base):
	"""Index of the most frequent words in a project by part of speech.

	Attributes:
		word
		word_id
		pos
		sentence_count
		project_id
	"""
	# fields
	word = db.Column(db.String)
	word_id = db.Column(db.Integer, db.ForeignKey("word.id", ondelete='CASCADE'))
	pos = db.Column(db.String)
	sentence_count = db.Column(db.Integer)
	project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete='CASCADE'))

class FrequentSequence(db.Model, Base):
	"""Index of the most frequent Sequences in a project

	Attributes:
		sequence
		sequence_id
		sentence_count
		project_id
	"""
	# fields
	sequence = db.Column(db.String)
	sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id", ondelete='CASCADE'))
	sentence_count = db.Column(db.Integer)
	project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete='CASCADE'))