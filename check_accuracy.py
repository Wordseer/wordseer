from sqlalchemy import create_engine
import sys
import os
import random

def check_documents(old_db, new_db):
	""" Check accuracy of documents

	Check the following:
	- title matching
	- sentence counts
	"""

	print("=== Documents ===\n")

	print("--- Check title ---\n")

	# Check title matching
	title_query_old = """
		SELECT LOWER(title) as title
		FROM document
		ORDER BY LOWER(title)
	"""

	title_query_new = """
		SELECT LOWER(title)
		FROM document
		ORDER BY LOWER(title)
	"""

	result = list(old_db.execute(title_query_old))

	for row in result: print("\t" + str(row.title))

def check_sentences(old_db, new_db):
	"""Check the accuracy of sentences by randomized testing

	Check the following:
	- text matching
	"""

	print("=== Sentences ===")

	ids_old = get_random_id_from("sentence", old_db, 20)

	sentences_old = old_db.execute(
		"""
			SELECT *
			FROM sentence
			WHERE id in {ids}
		""".format(ids = ids_old)
	).fetchall()

	print("--- Check matching text ---")

	print("--- Check words ---")

	words_old = [
		old_db.execute(
			"""
				SELECT word.word as word, sentence_xref_word.position as position
				FROM word INNER JOIN sentence_xref_word
				ON word.id = sentence_xref_word.word_id
				WHERE sentence_xref_word.sentence_id = {sentence_id}
			""".format(sentence_id=sentence_id)
		).fetchall()
		for sentence_id in ids_old
	]

	for words in words_old: 
		print("\n")
		sorted_words_old = [
			word[0] for word in
			sorted(words, key=lambda x: x[1])
		]

		print(sorted_words_old)

	print("--- Check dependencies ---")

	dependencies_old = [
		old_db.execute(
			"""
				SELECT
					dependency.gov as governor,
					dependency.dep as dependent,
					dependency.relationship as relationship
				FROM dependency
					INNER JOIN dependency_xref_sentence
						ON dependency.id = dependency_xref_sentence.dependency_id
				WHERE dependency_xref_sentence.sentence_id = {sentence_id}
			""".format(sentence_id=sentence_id)
		).fetchall()
		for sentence_id in ids_old
	]

	for dep in dependencies_old: print("\t"+str(dep))

# Helpers

def get_random_id_from(table, db, n=1):

	ids = []

	for i in range(0, n):

		count_query = """
			SELECT COUNT(*) as count
			FROM {table}
		""".format(table = table)

		count = db.execute(count_query).fetchone().count

		random_index = random.randint(0, count-1)

		id_query = """
			SELECT id
			FROM {table}
		""".format(table = table)

		ids.append(int(db.execute(id_query).fetchall()[random_index].id))

	if n == 1:
		return ids[0]
	else:
		return tuple(ids)

# Main

if __name__ == "__main__":

	root = os.path.abspath(os.path.dirname(__file__))

	# Read the args and connect to the databases
	old_db = create_engine("mysql://keien@localhost/" + sys.argv[1])
	new_db = None # create_engine("sqlite://" + os.path.join(root, sys.argv[2]))

	# check_documents(old_db, new_db)
	check_sentences(old_db, new_db)