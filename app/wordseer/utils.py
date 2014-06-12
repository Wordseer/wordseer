"""
Various utilities for use in the view methods.
"""
import pdb

from flask import request

from .models import SequenceSet
from .models import sequences_in_sequencesets
from app import app
from app import db
from app.uploader.models import Sentence
from app.uploader.models import Sequence
from app.uploader.models import Word

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

def get_relation_description(relation):
    """Do we really need this method? What exactly does it do?

    Arguments:
        relation (str):
    """
    #TODO: evaluate this method's usefulness
    #TODO: unit testing
    if "none" in relation:
        return ""
    if "" in relation:
        return "(any relation)"
    if "agent subj nsubj csubj nsubjpass csubjpass" in relation:
        return "agent subj nsubj xsubj csubj nusbjpass csubjpass"
    if "obj dobj iobj pobj" in relation:
        return "dobj iobj pobj"
    else:
        return relation

def remove_spaces_around_punctuation(sentence):
    """Remove spaces before certain punctuation marks and after certain other
    ones.

    Which marks shouldn't have a space before and which shouldn't have one
    after are defined in ``config.py``.

    Arguments:
        sentence (str): The sentence to remove spaces around punctuation in.

    Returns:
        str: The given sentence with punctuation stripped before and after
        certain punctuation marks.
    """

    for mark in app.config["PUNCTUATION_NO_SPACE_BEFORE"]:
        sentence = sentence.replace(" " + mark, mark)

    for mark in app.config["PUNCTUATION_NO_SPACE_AFTER"]:
        sentence = sentence.replace(mark + " ", mark)

    return sentence

#TODO: needs clarification
def get_words_in_sentence(sentence_id):
    """Given a ``Sentence`` ID, return information about all ``Word``s in that
    sentence in the form of a list.

    The structure of the list is like this::

        [
            {
                "word": "foo" # str: the surface word
                "word_id": 5 # int: the id of the word
                "space_after": " " # str: the space after the word, if any
                "phrase_set": # ???
            }
            ...etc...
        ]


    Arguments:
        sentence_id (int): The ID of the sentence to query.
    """
    pass

#TODO: needs clarification
def get_phrase_set_memberships():
    pass

#TODO: needs clarification
def get_relation_id(relation):
    pass

#TODO: unit test
def get_word_ids_from_surface_word(word):
    """Return a list of ``Word`` IDs that correspond to the given surface word.

    A surface word could have multiple IDs if it has different possible
    lemmas depending on context.

    TODO: what does lemmatize do?

    Arguments:
        word (str): The word to query for.

    Returns:
        list of ints: A list of ``Word`` IDs.
    """
    lemmatize = request.args.get("all_word_forms") == "on"
    word = word.strip()

    if not lemmatize:
        if not "*" in word:
            words = Word.query.filter(Word.word == word.strip()).all()
        else:
            words = Word.query.\
                filter(Word.word.like(query_word.replace("*", "%"))).all()

        return [word.id for word in words]

    else:
        return get_lemma_variant_ids(word)

#TODO: What are these tables?
def get_dependency_ids(gov, dep, relation, start, limit, in_document=[],
    in_table=None, in_sentence=[]):
    """Get dependencies that match the given criteria.

    Arguments:
        gov (str): The governor to match, as a string.
        dep (str): The dependency to match, as a string.
        in_document (list of ints): Retrieve only dependencies from units with
            one of these IDs.
        in_table (str): Retrieve only dependencies from this table.
        in_sentence (list of ints): Retrieve only dependencies from units with
            one of these IDs.

    Returns:
        ???
    """
    pass

# TODO: depends on get_relation_id
def relationship_id_list(words):
    pass

#TODO: can this accept and return a list instead?
#TODO: depends on get_phrase_id_string
def word_id_list(raw_words):
    """Convert a list of words to a list of ``Word`` IDs.

    Arguments:
        raw_words (str): A list of words to look up.

    Returns:
        str: A comma separated list of IDs for all the words given.
    """

    #raw_words = [raw_word.replace("+", "").strip() for raw_word in raw_words]
    words = words.replace("+", "").strip()
    if words:
        word_list = words.split(" ")
        if "," in words:
            word_list = words.split(",")

    pass

def sequence_id_list(words):
    """Convert a list of words or phrases to a list of sequence IDs.
    """
    pass

#TODO: needs clarification
def get_words_from_sequence_set(phrase_set_id):
    """Return a string with all the words in the given word set ID.
    """

    lemmatize = request.args.get("all_word_forms") == "on"

    words = db.session.query(Word).join(SequenceSet).distinct().\
        filter(SequenceSet.id == sequence_set_id)

#TODO: merge with above?
#Because we're using this ORM, getting words or word ids or whatever else
#from Word objects is trivial, and list comprehensions make lists easy to make.
def get_word_ids_from_sequence_set(sequence_set_id):
    """Returns a list containing all the ``Word` IDs in the given
    ``SequenceSet``.

    Args:
        sequence_set_id (int): The ID of the ``SequenceSet`` to retrieve word
            IDs from.

    Returns:
        list: A list of every ``Word`` ID present in the given ``SequenceSet``.
    """

    lemmatize = request.args.get("all_word_forms") == "on"
    sequences = db.session.query(Sequence).\
        join(sequences_in_sequencesets).\
        distinct().\
        filter(sequences_in_sequencesets.c.sequenceset_id == sequence_set_id).\
        all()
    pdb.set_trace()

    ids = []

    for sequence in sequences:
        for word in sequence.words:
            if lemmatize:
                ids.extend(get_lemma_variant_ids(word.word))
            else:
                ids.append(word.id)
    return list(set(ids))

def get_lemma_variant_ids(surface_word):
    """Get ``Word`` IDs for all words that have the same lemma as this one.

    That is, get the list of all lemmas whose surface word is ``surface_word``
    and then return the IDs of all ``Word``s that have those lemmas.

    Arguments:
        surface_word (str): The surface word to query.

    Returns:
        list: A list of IDs from ``Word`` objects with the same lemma as
        the given word.
    """
    surface_word = surface_word.strip()
    lemmas = db.session.query(Word).\
        filter(Word.word == surface_word).\
        all()

    lemma_list = [word.lemma for word in lemmas]

    words = db.session.query(Word.id).\
        filter(Word.lemma.in_(lemma_list)).\
        all()

    return [word.id for word in words]

#TODO: merge with above?
def get_lemma_variants(surface_word):
    """Get the ``word`` attributes of ``Word``s that all have the same lemma
    as the given word.

    Arguments:
        surface_word (str): The surface word to query.

    Returns:
        list: A list of ``word`` attributes from ``Word`` objects with the same
        lemma as the given word.
    """

    lemmas = db.session.query(Word).\
        filter(Word.word == surface_word).\
        all()

    lemma_list = [word.lemma for word in lemmas]

    words = db.session.query(Word).\
        distinct().\
        filter(Word.lemma.in_(lemma_list)).\
        all()

    return [word.word for word in words]

#TODO: need clarification
def make_query_string(gov, govtype, dep, deptype, relation, collection,
    metadata, phrases):
    """Return a string representing the query in a human-friendly way.
    """
    pass

#TODO: cached_filtered_sent_ids vs filtered_sent_ids
def get_number_of_sentences_in_slice():
    pass

#TODO: filtered_sent_ids vs cached_filtered_sent_ids
def get_number_of_documents_in_slice():
    pass

