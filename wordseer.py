#!/usr/bin/env python

"""
Run the wordseer_flask website.
"""

from app import app

if __name__ == '__main__':
#    app.debug = True
    app.run(debug=True)
