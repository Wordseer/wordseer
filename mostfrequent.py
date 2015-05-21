"""script to compute the most frequent words for a given project
"""
from sqlalchemy import func
from sqlalchemy.sql.expression import desc

from app import app, db
from app.models import FrequentSequence, FrequentWord, Project, Sequence, SequenceCount, Word, WordCount

STOPWORDS = app.config["STOPWORDS"]

def get_frequent_words_for_project(proj_id, pos):
	"""POS values: `NN`, `VB`, `JJ`
	"""
	project = Project.query.get(proj_id)
	like_query = pos + "%"

	words_query = db.session.query(
	    Word.id,
	    Word.surface.label("word"),
	    WordCount.sentence_count.label("sentence_count")
    ).\
		filter(WordCount.project_id == project.id).\
		filter(WordCount.word_id == Word.id).\
		filter(Word.part_of_speech.like(like_query)).\
		filter(~Word.lemma.in_(STOPWORDS)).\
		filter(~Word.surface.in_(STOPWORDS)).\
		order_by(desc("sentence_count")).\
		limit(20)

	for word in words_query:
	    freqword = FrequentWord(word=word.word, word_id=word.id, pos=pos, 
	    	sentence_count=word.sentence_count, project_id=proj_id)
	    freqword.save()

def get_frequent_sequences_for_project(proj_id, length):
	project = Project.query.get(proj_id)

	sequence_query = db.session.query(
        Sequence.id,
        Sequence.has_function_words.label("has_function_words"),
        Sequence.sequence.label("text"),
        SequenceCount.sentence_count.label("sentence_count"),
    ).\
	    filter(SequenceCount.project_id == project.id).\
	    filter(SequenceCount.sequence_id == Sequence.id).\
	    filter(Sequence.length == length).\
	    filter(Sequence.lemmatized == False).\
	    filter(Sequence.has_function_words == False).\
	    order_by(desc("sentence_count")).\
	    limit(30)

	for seq in sequence_query:
	    freqseq = FrequentSequence(sequence=seq.text, sequence_id=seq.id, 
	    	sentence_count=seq.sentence_count, project_id=proj_id)
	    freqseq.save()

def main():
	
	#frequent words
	parts_of_speech = ('NN', 'VB', 'JJ')
	db.session.query(FrequentWord).\
		filter(FrequentWord.project_id == 3).\
		delete()
	for pos in parts_of_speech:
		get_frequent_words_for_project(3, pos)
	print "frequent word results:", FrequentWord.query.count()

	#frequent sequences
	db.session.query(FrequentSequence).\
		filter(FrequentSequence.project_id == 3).\
		delete()
	get_frequent_sequences_for_project(3, 2)
	print "frequent sequence results:", FrequentSequence.query.count()

if __name__ == '__main__':
	main()