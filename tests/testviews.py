"""tests for the ``app.wordseer.views`` package"""

import unittest

from app import models, db
from flask import json

import database
import wordseer


class TestSetViews(unittest.TestCase):
    """test all the different ``Set`` views"""

    def setUp(self):
        """doc"""
        self.longMessage = True

        self.client = wordseer.app.test_client()

        database.restore_cache()

        self.user = models.flask_security.User()

        db.session.add(self.user)

        self.set1 = models.sets.SentenceSet(name="test1", user=self.user)
        self.set2 = models.sets.SequenceSet(name="test2", parent=self.set1,
            user=self.user)
        self.set3 = models.sets.SentenceSet(name="test3", parent=self.set1,
            user=self.user)
        self.set4 = models.sets.SentenceSet(name="test4", parent=self.set1,
            user=self.user)
        self.set5 = models.sets.DocumentSet(name="test5", user=self.user)


        db.session.add_all([self.set1, self.set2, self.set3, self.set4,
            self.set5])

        db.session.commit()

        db.session.refresh(self.user)
        db.session.refresh(self.set1)
        db.session.refresh(self.set3)
        db.session.refresh(self.set4)

        # am I adding users correctly?
        assert self.set1.user_id == self.user.id, \
            "set: %s, user: %s" % (self.set1.user_id, self.user.id)

        # am I adding parents correctly?
        assert self.set3.parent_id == self.set1.id, \
            "%s, %s" % (self.set3.parent_id, self.set1.id)

    @classmethod
    def tearDownClass(self):
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
            # TODO: creation dates should be defaulting to current in model
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

            # test responses
            self.assertEqual(response.mimetype, "application/json",
                msg=response.mimetype)
            data = json.loads(response.data)
            self.assertEqual(data["root"], True)
            self.assertEqual(len(data["children"]), 1, msg=data)

            # first level nesting
            self.assertEqual(data["children"][0]["text"], "test1")

            # second level nesting
            self.assertEqual(data["children"][0]["children"][0]["text"],
                "test3", msg=data)
            self.assertEqual(data["children"][0]["children"][1]["text"],
                "test4", msg=data)

    def test_list_flat(self):
        """test the ``sets.CRUD.list_flat`` method"""

        with self.client as c:
            # required variables
            response = c.get("/api/sets/?instance=foo&type=listflat")
            self.assertEqual(response.status_code, 400)

            # should work
            query = "?instance=foo&type=listflat&collectiontype=sentenceset&user="\
                + str(self.user.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 200)

            # test responses
            self.assertEqual(response.mimetype, "application/json",
                msg=response.mimetype)
            data = json.loads(response.data)
            self.assertEqual(data["sets"][0]["text"], "test1")
            self.assertEqual(data["sets"][2]["text"], "test4")

            # is document "all" set prepended?
            query = "?instance=foo&type=listflat&collectiontype=documentset&user="\
                + str(self.user.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["sets"][0]["text"], "all", msg=data)

    def test_create(self):
        """test the ``sets.CRUD.create`` method"""

        with self.client as c:
            # required variables
            response = c.get("/api/sets/?instance=foo&type=create")
            self.assertEqual(response.status_code, 400)

            # should work
            query = "?instance=foo&type=create&collectiontype=sentenceset" \
                + "&user=" + str(self.user.id) + "&name=test_create&parent=0"
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)

            # TODO: dates not being set
            self.assertEqual(data["date"], None, msg=data)

            # may need to change if more rows are added to setup method
            new_id = 6
            self.assertEqual(data["id"], new_id, msg=data)

            # make sure it went into db correctly by reading it
            new_set = c.get("/api/sets/?instance=foo&type=read&id=" + str(new_id))
            data = json.loads(new_set.data)
            self.assertEqual(data["text"], "test_create", msg=data)

    def test_delete(self):
        "test the ``sets.CRUD.delete`` method"

        with self.client as c:
            # required variables
            # required variables
            response = c.get("/api/sets/?instance=foo&type=delete")
            self.assertEqual(response.status_code, 400)

            # delete a root note, see what happens
            query = "?instance=foo&type=delete&id=" + str(self.set1.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 200)

            # is it gone?
            query = "?instance=foo&type=read&id=" + str(self.set1.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 400, msg=response.data)

            # what about children?
            query = "?instance=foo&type=read&id=" + str(self.set3.id)
            response = c.get("/api/sets/" + query)
            self.assertEqual(response.status_code, 400,
                msg="requires a delete-orphan cascade at the model level")
