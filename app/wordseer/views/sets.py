import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class CRUD(View):
    """CRUD Sets"""
    def __init__(self):
        """initialize variables needed for Set operations

        arguments:
        instance (str):
        type (str): Required
        id (int): Required if type in ["read", "delete"]
            or if type in ["update"] and update in ["add", "delete", "rename",
            "move","merge"]
        collectiontype (str): Required if type in ["list", "listflat", "create"]
        user (str): Required if type in ["list", "listflat", "create"]
            or type in ["update"] and update in ["addNote", "addTag"]
        name (str): Required if type in ["create"]
        parent (?): Required if type in ["create"]
        update(str): Required if type in ["update"]
        item  (int): Required if type in ["update"] and update in ["add",
            "delete", "addNote", "addTag", "deleteNote", "deleteTag"]
        annotation (?): Required if type in ["update"] and update in ["addNote",
            "addTag"]
        itemtype (str): Required if type in ["update"] and update
            in ["addNote", "addTag"]
        note_id (int): Required if type in ["update"] and update in ["editNote"]
        text (str): Required if type in ["update"] and update in ["editNote"]
        new_name (str): Required if type in ["update"] and update in ["rename"]
        new_parent (?): Required if type in ["update"] and update in ["move"]
        merge_into (?): Required if type in ["update"] and update in ["merge"]
        """
