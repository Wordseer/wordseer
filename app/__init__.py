from flask import Flask
from flask_wtf.csrf import CsrfProtect

from app.controllers import *
from app.models import *

app = Flask(__name__)

app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CsrfProtect(app)
