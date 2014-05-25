"""Word frequencies and bar charts
"""

from flask import request
from flask.json import JSONDecoder
from flask.json import JSONEncoder
from flask.views import View
from sqlalchemy.sql import func

from app import app
from app import db
from . import utils
from . import models

PAGE_SIZE = 100

class WordFrequencies(object):
    def dispatch(self):
        """Dispatch the request to this page.
        """

        words = request.args.get(words)
        page = request.args.get(page)

        if page:
            results = self.get_word_frequencies(words.replace("*", "%"), page)
            return JSONEncoder(results)

    def get_word_frequencies(self, words, page):
        answer = {}
        offset = page * PAGE_SIZE

        if words:
            wordlist = words.split(",")
            for word in wordlist:
                #TODO: this query might need work
                result = db.session.query(models.Word.sentences,
                    func.count('*').label("sentence_count")).\
                    order_by(models.Word.sentences.desc()).subquery().\
                    filter(models.Word.word.like(word)).\
                    limit(PAGE_SIZE).offset(offset).all()

                for row in result:
                    answer.append({
                        "id": row["id"],
                        "word": row["word"],
                        "pos": row["pos"],
                        "sentence_count": row["sentence_count"],
                    })
        else:
            result = db.session.query(models.Word.sentences,
                func.count('*').label("sentence_count")).\
                order_by(models.Word.sentences.desc()).subquery().\
                limit(PAGE_SIZE).offset(offset).all()

            for row in result:
                answer.append({
                    "id": row["id"],
                    "word": row["word"],
                    "pos": row["pos"],
                    "sentence_count": row["sentence_count"],
                })

        return answer
