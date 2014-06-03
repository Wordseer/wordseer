"""Word frequencies and bar charts
"""

from flask import request
from flask import abort
from flask.json import jsonify
from flask.views import View
from sqlalchemy.sql import func

from app import app
from app import db
from .. import wordseer
from .. import utils
from ...uploader.models import Word
from ...uploader.models import word_in_sentence

@wordseer.route("/word-frequencies/get-frequent-words")
def get_word_frequencies():
    """Use the functions in this file to return a JSON response.

    Arguments:
        words (str): The words to retrieve frequencies for, separated by commas.
        page (int): Which page of results to retrieve (see
            ``get_word_frequencies`` documentation).

    Returns:
        If the request is successful, then it returns a JSON response as a
        string. This response has the following structure::

            {"result":
                [
                    {
                        "id": int,
                        "word": str,
                        "pos": int,
                        "sentence_count": int
                    }
                    ...and so on...
                ]
            }

        Further details on the return value can be found in the
        ``get_word_frequencies`` documentation.

        If the required arguments (listed above) are not supplied, then a 400
        error is returned.
    """

    words = request.args.get("words", "")
    try:
        page = int(request.args["page"])
    except (KeyError, ValueError):
        abort(400)

    results = get_word_frequency_page(words, page)
    return jsonify(results=results)

def get_word_frequency_page(words, page):
    """Get the frequencies of the given words, returning the given page
    of the pagination.

    Note that the ``page`` argument signifies the "page" for every word
    individually. That is, if you have three words (``foo``, ``bar``, ``baz``)
    and a page size of 1, and you query with ``words=foo,bar,baz&page=1`` you
    will get no results. This is because there is one page of results each for
    ``foo``, ``bar``, and ``baz``. A query like ``words=foo,bar,baz&page=0``
    will return data for both ``foo``, ``bar``, and ``baz``.

    Arguments:
        words (string): A string of comma separated words.
        page (int): This function automatically paginates the result
            of the database query. Each page contains ``PAGE_SIZE`` number
            of entries, a config variable set in ``config.py``. This is zero
            indexed.

    Retruns:
        list: A list in which every item is a dict which holds the id,
            word, pos, and length of the sentences attributes of every
            word retrieved from the database.
    """
    #TODO: simplify the query, simplify the dict setting
    answer = []
    offset = page * app.config["PAGE_SIZE"]

    if words:
        wordlist = words.split(",")

        for word in wordlist:
            result = db.session.query(Word,
                func.count(word_in_sentence.c.word_id).label("sentences")
            ).join(word_in_sentence).\
                filter(Word.word.like(word)).\
                group_by(Word).\
                order_by("sentences").\
                limit(app.config["PAGE_SIZE"]).\
                offset(offset).\
                all()

            for word in result:
                answer.append({
                    "id": word[0].id,
                    "word": word[0].word,
                    "pos": word[0].pos,
                    "sentence_count": word.sentences
                })
    else:
        result = db.session.query(Word,
            func.count(word_in_sentence.c.word_id).label("sentences")
        ).join(word_in_sentence).\
            group_by(Word).\
            order_by("sentences").\
            limit(app.config["PAGE_SIZE"]).\
            offset(offset).\
            all()

        for word in result:
            answer.append({
                "id": word[0].id,
                "word": word[0].word,
                "pos": word[0].pos,
                "sentence_count": word.sentences
            })

    return answer

