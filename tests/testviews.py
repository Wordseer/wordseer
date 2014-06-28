"""tests for the ``app.wordseer.views`` package"""

import unittest

from app import models, db
from flask import json

import database
import wordseer


class TestSetViews(unittest.TestCase):
    """test all the different ``Set`` views"""

    @classmethod
    def setUpClass(cls):
        """doc"""
        cls.longMessage = True

        cls.client = wordseer.app.test_client()

        database.restore_cache()

        cls.user = models.flask_security.User()

        db.session.add(cls.user)

        cls.set1 = models.sets.SentenceSet(name="test1", user=cls.user)
        cls.set2 = models.sets.SequenceSet(name="test2", parent=cls.set1,
            user=cls.user)
        cls.set3 = models.sets.SentenceSet(name="test3", parent=cls.set1,
            user=cls.user)

        db.session.add_all([cls.set1, cls.set2, cls.set3])

        db.session.commit()

        db.session.refresh(cls.user)
        db.session.refresh(cls.set1)
        db.session.refresh(cls.set3)

        # am I adding users correctly?
        assert cls.set1.user_id == cls.user.id, \
            "set: %s, user: %s" % (cls.set1.user_id, cls.user.id)

        # am I adding parents correctly?
        assert cls.set3.parent_id == cls.set1.id, \
            "%s, %s" % (cls.set3.parent_id, cls.set1.id)

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def test_crud_init(self):
        """test the ``sets.CRUD`` class __init__"""
        with self.client as c:
            response = c.get("/api/sets/")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

            response = c.get("/api/sets/?instance=bar")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

    def test_read(self):
        """test the ``sets.CRUD.read`` view"""

        with self.client as c:
            # missing required variables
            response = c.get("/api/sets/?instance=foo&type=read")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

            # should work
            # db.session.refresh(self.set1)
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

    def test_list(self):
        """test the ``sets.CRUD.list`` view"""

        with self.client as c:
            # required variables
            response = c.get("/api/sets/?instance=foo&type=list")
            self.assertEqual(response.status_code, 400)

            #should work
            query = "?instance=foo&type=list&collectiontype=sentenceset&user="\
                + str(self.user.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 200)

            # TODO: test responses
            self.assertEqual(response.mimetype, "application/json",
                msg=response.mimetype)
            data = json.loads(response.data)
            self.assertEqual(data["root"], True)
            self.assertEqual(len(data["children"]), 1, msg=data)
