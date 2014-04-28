# A Flask-based back end for WordSeer

This is the server-side code for the WordSeer application, written in Python
using the Flask framework and several web framework libraries.

## Running the application
1.  Create a virtualenv
2.  Run:

        bash flask_packages

    to install the necessary packages.
3.  Run:

        python database.py create

    to create the dabase, and

        python database.py migrate

    to migrate the model schema into the database.

## Testing
1. Simply run `runtests.py`:

    python runtests.py
