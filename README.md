# A Flask-based back end for WordSeer

[WordSeer](http://wordseer.berkeley.edu/) is a tool for natural language
analysis of digital corpora. This repository is a rewrite of the [original 
implementation](https://bitbucket.org/silverasm/wordseer/overview) into python
from PHP.

This is the server-side and web interface code for the WordSeer application,
written in Python using the Flask framework and several web framework libraries.

## Running the application
1.  Create a virtualenv
2.  Run:

        pip -r requirements.txt

    to install the necessary packages.
3.  Run:

        python database.py create

    to create the dabase, and

        python database.py migrate

    to migrate the model schema into the database.

## Testing
1. Simply run `runtests.py`:

        python runtests.py

