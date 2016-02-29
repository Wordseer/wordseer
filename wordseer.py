#!/usr/bin/env python

"""Run the wordseer_flask website.
"""
import os
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0')
