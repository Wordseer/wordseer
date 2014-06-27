"""tests for the ``app.wordseer.views`` package"""

import unittest

from app import models, db
from flask import json

import wordseer


class TestSetViews(unittest.TestCase):
    """test all the different ``Set`` views"""

    def setUp(self):
        self.app = wordseer.app

        # create some Sets to query
        user = models.flask_security.User()
        db.session.add(user)
        set1 = models.sets.SentenceSet(name="test1", user_id=user.id)
        db.session.add(set1)
        set2 = models.sets.SequenceSet(name="test2", parent_id=set1.id,
            user_id=user.id)
        db.session.add(set2)
        set3 = models.sets.SentenceSet(name="test3", parent_id=set1.id,
            user_id=user.id)
        db.session.commit()

        self.user = user
        self.set1 = set1
        self.set2 = set2
        self.set3 = set3

    def test_crud_init(self):
        """test the ``sets.CRUD`` class __init__"""
        with self.app.test_client() as c:
            response = c.get("/api/sets/")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

            response = c.get("/api/sets/?instance=bar")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

    def test_read(self):
        """test the ``sets.CRUD.read`` view"""

        with self.app.test_client() as c:
            # missing required variables
            response = c.get("/api/sets/?instance=foo&type=read")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

            # should work
            response = c.get("/api/sets/?instance=foo&type=read&id=" +
                str(self.set1.id))
            self.assertEqual(response.status_code, 200, msg=response.status_code)

            # test for well-formed json response
            self.assertEqual(response.mimetype, "application/json",
                msg=response.mimetype)
            data = json.loads(response.data)
            self.assertEqual(data["text"], self.set1.name)
            self.assertEqual(data["type"], self.set1.type)
            self.assertEqual(data["id"], self.set1.id)
            self.assertEqual(data["date"], self.set1.creation_date)

            # TODO: 'ids' and 'phrases'
            # self.assertEqual(data["ids"], self.set1.name)

    def test_list(self):
        """test the ``sets.CRUD.list`` view"""

        with self.app.test_client() as c:
            # required variables
            response = c.get("/api/sets/?instance=foo&type=list")
            self.assertEqual(response.status_code, 400)

            #should work
            query = "?instance=foo&type=list&collectiontype=sentenceset&user="\
                + str(self.user.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 200)

            # TODO: test responses
