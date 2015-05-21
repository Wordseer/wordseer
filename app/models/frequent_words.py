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
	word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
	pos = db.Column(db.String)
	sentence_count = db.Column(db.Integer)
	project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

class FrequentSequence(db.Model, Base):
	"""Index of the most frequent Sequences in a project

	Attributes:
		text
		sequence_id
		sentence_count
		project_id
	"""
	pass