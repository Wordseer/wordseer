import os

from flask import Flask
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)

app.config.from_object('config')
CsrfProtect(app)

from app.views import *
from app.models import *
