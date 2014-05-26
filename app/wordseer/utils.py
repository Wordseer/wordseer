"""
Various utilities for use in the view methods.
"""

from flask import request

from app import app
from app import db
from . import models

def table_exists(table):
    """Check if the given table exists in the database.

    Args:
        table (str): A table to check for.

    Returns:
        boolean: ``True`` if it does, ``False`` otherwise.
    """
    existing_tables = db.metadata.tables.keys()

    try:
        existing_tables.index(table)
    except ValueError:
        return False
    return True

def get_name_from_relation(relation):
    """Given a relation, return a human-readable name. This method is configured
    using a dict in config.py.

    Args:
        relation (str): A relation to look up (as the key) in the RELATIONS dict
            in config.py.

    Returns:
        string: The human-readable relation name, the value of the key that is
            ``relation``.
    """
    for relations, name in app.config["RELATIONS"].iteritems():
        if relation in relations:
            return name

def get_word_ids_from_phrase_set(phrase_set_id):
    """Returns a string containing all the words in the given
    phrase set ID.

    Args:
        phrase_set_id (int): The ID of the phrase set to retrieve word IDs from.

    Returns:
        list: A list of word IDs.
    """

    lemmatize = request.args.get("all_word_forms") == "on"

    #TODO: what are these strange new tables?
    pass

def get_word_ids(word):
    """Returns a list of all the IDs that correspond to a
	given surface word. A word can have multiple id's
	if it has different parts of speech.

    Args:
        word (str): The word to look up.

    Returns:
        list: A list of all the given word's IDs.
    """

    if request.args.get("all_word_forms") == "on":
        if not "*" in word:
            result = models.Word.query.filter(Word.word == word.strip()).all()
        else:
            query_word = word.replace("%", "*")
            result = models.Word.query.filter(Word.word.like(query_word)).all()

        if len(result):
            ids = []
            for row in result:
                ids.append(row.id)
            return ids

        else:
            return []

    else:
        return get_lemma_variant_ids(word)

def get_lemma_variant_ids(word):
    """Returns an array of word id's for all the words that have the same lemma
    as this one.

    Arguments:
        word (str): A word to get lemmas for.

    Returns:
        list: A list of the IDs of all known words with the same lemma.
    """

    word = word.trim()
    result = models.Word.query.filter(models.Word.word == word).all()
    lemmas = [word.lemma for word in result]

    if lemmas:
        result = models.Word.query.filter(models.Word.lemma in lemmas)
        return [word.id for word in result]

    return []

