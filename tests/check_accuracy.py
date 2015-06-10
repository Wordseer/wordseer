"""Usage::

    python check_accuracy.py mysql://<user>:<password>@<server>/<database> <path to sqlite db>
"""

from sqlalchemy import create_engine
import sys
import os
import random
import difflib

d = difflib.Differ()

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

def check_sentences(old_db, new_db, num_sentences=20):
	"""Check the accuracy of sentences by randomized testing

	Check the following:
	- text matching
	"""

	print("=== Sentences ===")

	matching_sentences = get_matching_sentences(old_db, new_db, num_sentences)
	sentences_old = matching_sentences["old"]
	sentences_new = matching_sentences["new"]

	sentences_old_texts = [ sentence.sentence.strip() for sentence in sentences_old ]
	sentences_new_texts = [ sentence.text for sentence in sentences_new if sentence ]

	for line in difflib.unified_diff(sentences_old_texts, sentences_new_texts, "old db", "new db"):
		print("\t" + line[:64])

	matches = len(sentences_new_texts)
	print("\n\t" + str(matches) + "/" + str(num_sentences) + " matches\n")

	sentence_accuracy = float(matches) / num_sentences

	print("--- Check words ---")

	sentence_ids_old = []
	sentence_ids_new = []

	for i in range(len(sentences_old)):
		if sentences_new[i] != None:
			sentence_ids_old.append(sentences_old[i].id)
			sentence_ids_new.append(sentences_new[i].id)

	words_old = [
		old_db.execute(
			"""
				SELECT word.id, word.word, word.sentence_count as sentence_count
				FROM word INNER JOIN sentence_xref_word
				ON word.id = sentence_xref_word.word_id
				WHERE sentence_xref_word.sentence_id = {sentence_id}
				ORDER BY sentence_xref_word.position
			""".format(sentence_id=sentence_id)
		).fetchall()
		for sentence_id in sentence_ids_old
	]

	words_new = [
		new_db.execute(
			"""
				SELECT word.id, word.word as word
				FROM word INNER JOIN word_in_sentence
				ON word.id = word_in_sentence.word_id
				WHERE word_in_sentence.sentence_id = {sentence_id}
				ORDER BY word_in_sentence.position
			""".format(sentence_id=sentence_id)
		).fetchall()
		for sentence_id in sentence_ids_new
	]

	words_old = [ [ word for word in words] for words in words_old ]
	words_new = [ [ word for word in words] for words in words_new ]

	mismatches = 0
	total = 0

	for i in range(0, len(words_old)):

		word_strings_old = [ word.word.lower() for word in words_old[i] ]
		word_strings_new = [ word.word.lower() for word in words_new[i] ]

		total += len(word_strings_old)

		diff = difflib.unified_diff(
			word_strings_old,
			word_strings_new,
			" ".join(word_strings_old)[:64],
			" ".join(word_strings_new)[:64]
		)

		for line in diff:
			print("\t" + str(line))

			# Count mismatches
			if (line[0] == "+" and line[1] != "+") or \
				(line[0] == "-" and line[1] != "-"):
				mismatches += 1

	print("\n\t" + '%s/%s' % (total-mismatches, total) + " matches\n")

	word_accuracy = float(total - mismatches) / total

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
		for sentence_id in sentence_ids_old
	]

	for i in range(len(dependencies_old)):
		for j in range(len(dependencies_old[i])):
			governor = dependencies_old[i][j].governor.lower()
			dependent = dependencies_old[i][j].dependent.lower()
			relationship = dependencies_old[i][j].relationship.lower()

			dependencies_old[i][j] = " ".join([governor, dependent, relationship])

	dependencies_new = [
		new_db.execute(
			"""
				SELECT
					dependency.governor_id as governor,
					dependency.dependent_id as dependent,
					dependency.grammatical_relationship_id as relationship
				FROM dependency
					INNER JOIN dependency_in_sentence
						ON dependency.id = dependency_in_sentence.dependency_id
				WHERE dependency_in_sentence.sentence_id = {sentence_id}
			""".format(sentence_id=sentence_id)
		).fetchall()
		for sentence_id in sentence_ids_new
	]

	for i in range(len(dependencies_new)):
		for j in range(len(dependencies_new[i])):
			governor_id = dependencies_new[i][j][0]
			dependent_id = dependencies_new[i][j][1]
			grammatical_relationship_id = dependencies_new[i][j][2]

			governor = new_db.execute("""
				SELECT word
				FROM word
				WHERE id = ?
			""", governor_id).fetchone().word.lower()

			dependent = new_db.execute("""
				SELECT word
				FROM word
				WHERE id = ?
			""", dependent_id).fetchone().word.lower()

			grammatical_relationship = new_db.execute("""
				SELECT name
				FROM grammatical_relationship
				WHERE id = ?
			""", grammatical_relationship_id).fetchone().name.lower().split("_")[0]

			dependencies_new[i][j] = " ".join([governor, dependent, grammatical_relationship])

	mismatches = 0
	total = 0

	for i in range(len(dependencies_new)):
		diff = difflib.unified_diff(
			sorted(dependencies_old[i]),
			sorted(dependencies_new[i]),
		)

		total += len(dependencies_old[i])

		for line in diff:
			print("\t" + str(line))

			# Count mismatches
			if (line[0] == "+" and line[1] != "+") or \
				(line[0] == "-" and line[1] != "-"):
				mismatches += 1

	print("\n\t" + '%s/%s' % (total-mismatches, total) + " matches\n")

	dependency_accuracy = float(total - mismatches) / total

	print("--- Check sequences ---")

	sequences_old = [
		old_db.execute("""
			SELECT sequence.sequence
			FROM sequence INNER JOIN sequence_xref_sentence
			ON sequence.id = sequence_xref_sentence.sequence_id
			WHERE sequence_xref_sentence.sentence_id = {sentence_id}
			ORDER BY sequence.sequence
		""".format(sentence_id=sentence_id)).fetchall()
		for sentence_id in sentence_ids_old
	]

	sequences_old = [ set([ sequence.sequence.lower() for sequence in sequences ]) for sequences in sequences_old ]

	sequences_new = [
		new_db.execute("""
			SELECT sequence.sequence
			FROM sequence INNER JOIN sequence_in_sentence
			ON sequence.id = sequence_in_sentence.sequence_id
			WHERE sequence_in_sentence.sentence_id = {sentence_id}
			ORDER BY sequence.sequence
		""".format(sentence_id=sentence_id)).fetchall()
		for sentence_id in sentence_ids_new
	]

	sequences_new = [ set([ sequence.sequence.lower() for sequence in sequences ]) for sequences in sequences_new ]

	mismatches = 0
	total = 0

	for i in range(len(sequences_old)):
		total += len(sequences_old[i])
		print("\tSequences missing in new db:")
		for item in sequences_old[i] - sequences_new[i]:
			print("\t\t" + str(item))
			mismatches += 1

		print("\tSequences missing in old db:")
		for item in sequences_new[i] - sequences_old[i]:
			print("\t\t" + str(item))
			mismatches += 1

		print("\n")


	print("\n\t" + '%s/%s' % (total-mismatches, total) + " matches\n")

	sequence_accuracy = float(total - mismatches) / total

	return {
		"words": word_accuracy,
		"dependencies": dependency_accuracy,
		"sequences": sequence_accuracy
	}


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

def get_matching_sentences(old_db, new_db, num_sentences):

	ids_old = get_random_id_from("sentence", old_db, num_sentences)

	sentences_old = [ sentence for sentence in old_db.execute(
		"""
			SELECT *
			FROM sentence
			WHERE id in {ids}
		""".format(ids = ids_old)
	).fetchall() ]

	print("--- Check matching text ---")

	sentences_old_texts = [ sentence.sentence.strip() for sentence in sentences_old ]

	sentences_new = [ new_db.execute(
		"""
			SELECT *
			FROM sentence
			WHERE sentence.text = ?
		""",
		sentence
	).fetchone() for sentence in sentences_old_texts ]

	return {
		"old": sentences_old,
		"new": sentences_new
	}

if __name__ == "__main__":
    root = os.path.join(os.path.realpath(__file__))

    # Read the args and connect to the databases
    old_db = create_engine(sys.argv[1])
    new_db = create_engine("sqlite:////" + os.path.join(sys.argv[2]))

    # check_documents(old_db, new_db)
    accuracies = check_sentences(old_db, new_db, 100)
    print(accuracies)

