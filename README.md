# A Flask-based back end for WordSeer

[![Stories in Ready](https://badge.waffle.io/wordseer/wordseer_flask.png?label=ready&title=Ready)](https://waffle.io/wordseer/wordseer_flask)
[![Build Status](https://travis-ci.org/Wordseer/wordseer_flask.svg?branch=master)](https://travis-ci.org/Wordseer/wordseer_flask)
[![Documentation](https://readthedocs.org/projects/wordseer-flask/badge/?version=latest)](http://wordseer-flask.readthedocs.org/en/latest/)

[WordSeer](http://wordseer.berkeley.edu/) is a tool for natural language
analysis of digital corpora.

There are two parts to this repository.

1. A rewrite of the
[original implementation](https://bitbucket.org/silverasm/wordseer/overview)
of wordseer into python from PHP.

    This is located in `app/wordseer/`. It is the server-side and web interface
    code for the WordSeer application, written in Python using the Flask
    framework and several web framework libraries.


2. An implementation of
[wordseerbackend](https://bitbucket.org/silverasm/wordseerbackend/overview) in
more maintainable python.

    This is located in `app/preprocessor/`. It is the pipeline or
    preprocessing code for uploaded data sets.

## Installation

### Prerequisites

The following packages must be installed before performing any setup:

- [Python 2.7](https://python.org/download)
- [Java 1.6 or later](https://www.java.com/en/download/manual.jsp)

### Linux/OS X install

Run `install.py` like so:

    ./install.py -i

This will launch the interactive installer which will guide you through the
simple installation process.

If you know what you want, run `install.py -h` to view known console flags.

### Windows

We also recommend installing the python dependencies (discussed below) in a
[virtual environment](https://pypi.python.org/pypi/virtualenv).

    pip install virtualenv
    virtualenv venv
    source venv/bin/activate

#### Installing the application
1.  Run:

        pip -r install requirements_win.txt

    to install the necessary packages.

3.  Run:

        python database.py create

    to create the dabase, and

        python database.py migrate

    to migrate the model schema into the database.

### Installing the preprocessor

1. `corenlp` must be installed manually. Clone the repository:

        git clone https://github.com/silverasm/stanford-corenlp-python.git
        cd stanford-corenlp-python
        python setup.py install

    This should install `corenlp` to your system.

2. In order to complete the setup, version *3.2.0* of Stanford's CoreNLP
library must simply be in a directory accessible to the backend. Download
[this file](http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip)
and move it to the root of the repository. Extract it and rename the folder
from `stanford-corenlp-full-2013-06-20` to `stanford-corenlp`.

3. If you followed the above directions, then you shouldn't need to worry about
any configuration. If you installed Stanford's CoreNLP elsewhere, then make sure
you edit `lib/wordseerbackend/wordseerbackend/config.py` for your setup.
Particularly make sure to point `CORE_NLP_DIR` to the Stanford NLP library.

4. Run the following command in the console:

        python -m nltk.downloader punkt

    You should then be ready to parse files. Example XML and JSON files are
    included in `tests/data`.

## Documentation
Documentation is
[available on readthedocs](http://wordseer-flask.readthedocs.org). You can also
build it yourself:

	cd docs/
	make html

Or, on windows, simply run `make.bat` in the same directory.

## Testing
Simply run `runtests.py`:

    python runtests.py

