#!/usr/bin/env python

"""Run the wordseer_flask website.
"""
from sys import argv

from app import app

if __name__ == '__main__':
    if len(argv) > 1:
        port = int(argv[1])
    else:
        port = None
    
    app.run(host='0.0.0.0', port=port)
