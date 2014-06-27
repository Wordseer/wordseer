"""tests for the ``app.wordseer.views`` package"""

import unittest

from app import models, db

import wordseer


class TestSetViews(unittest.TestCase):
    """test all the difference ``Set`` views"""

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
        set = models.sets.Set(id=1, name="set", type="sequenceset")
        db.session.add(set)

        # request it
        with self.app.test_client() as c:
            response = c.get("/api/sets/?instance=foo&type=read&id=1")
            self.assertEqual(response.status_code, 200, msg=response.status_code)
