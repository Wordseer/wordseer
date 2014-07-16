import json

from flask import abort
from flask import request
from flask.json import jsonify
from flask.views import View

from app import app
from app import db
from .. import wordseer
from .. import helpers


class UserView(View):
    """Called by signIn in user.js in service of
    all main application web pages, to handle user authentication.
    Returns a JSON object containing user data or information about
    errors."""
    # php equivalent: user/user.php
    
    def __init__(self, operation):
        """deal with all the variables"""
        # for use in dispatch_request
        self.operation = operation

    def dispatch_request(self):
        operations = {
            
        }

        result = operations[self.operation](self)
        return jsonify(result)