from flask import render_template, request

from app import app
from .. import models
from .. import forms

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
