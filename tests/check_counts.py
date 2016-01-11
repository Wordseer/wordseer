if __name__ == "__main__":

    root = os.path.join("home", "keien", "dev", "wordseer_flask")

    # Read the args and connect to the databases
    old_db = create_engine("mysql://keien@localhost/" + sys.argv[1])
    new_db = create_engine("sqlite:////" + os.path.join(root, sys.argv[2]))

    # Pick some sentences from new database
    sentence_ids = get_random_id_from("sentence", new_db, 50)
    sentence_texts = [ Sentence.query.get(id).text for id in sentence_ids ]

    # Find matches in the old database
    matched_sentences = [ old_db.execute(
        """
            SELECT *
            FROM sentence
            WHERE sentence.sentence = ?
        """,
        sentence
    ).fetchone() for sentence in sentences_old_texts ]

    print(matched_sentences)

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

