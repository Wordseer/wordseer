"""tests for the ``app.wordseer.views`` package"""

import unittest

from app import models, db
from flask import json

import wordseer


class TestSetViews(unittest.TestCase):
    """test all the different ``Set`` views"""

    app = wordseer.app

    def test_crud_init(self):
        """test that CRUD class instantiates with required variables"""
        with self.app.test_client() as c:
            response = c.get("/api/sets/")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

            response = c.get("/api/sets/?instance=bar")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

    def test_read(self):
        """test that the read function pulls correct variables and works"""
        # load up a ``Set``
        set = models.sets.SequenceSet(name="viewtest1")
        db.session.add(set)
        db.session.commit()

        # request it
        with self.app.test_client() as c:
            # missing required variables
            response = c.get("/api/sets/?instance=foo&type=read")
            self.assertEqual(response.status_code, 400, msg=response.status_code)

            # should work
            response = c.get("/api/sets/?instance=foo&type=read&id=" + str(set.id))
            self.assertEqual(response.status_code, 200, msg=response.status_code)

            # test for well-formed json response
            self.assertEqual(response.mimetype, "application/json",
                msg=response.mimetype)
            data = json.loads(response.data)
            self.assertEqual(data["text"], "viewtest1")
            self.assertEqual(data["type"], "sequenceset")
