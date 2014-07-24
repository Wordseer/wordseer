# A Flask-based back end for WordSeer

[![Stories in Ready](https://badge.waffle.io/wordseer/wordseer_flask.png?label=ready&title=Ready)](https://waffle.io/wordseer/wordseer_flask)
[![Build Status](https://travis-ci.org/Wordseer/wordseer_flask.svg?branch=master)](https://travis-ci.org/Wordseer/wordseer_flask)


[WordSeer](http://wordseer.berkeley.edu/) is a tool for natural language
analysis of digital corpora.

There are two parts to this repository.

1. A rewrite of the
[original implementation](https://bitbucket.org/silverasm/wordseer/overview)
of wordseer into python from PHP.

    This is located in `app/`. It is the server-side and web interface code for
    the WordSeer application, written in Python using the Flask framework and
    several web framework libraries.


2. An implementation of
[wordseerbackend](https://bitbucket.org/silverasm/wordseerbackend/overview) in
more maintainable python.

    This is located in `lib/wordseerbackend/`. It is the pipeline or
    preprocessing code for uploaded data sets.

## Installation

### Linux/OSX quick install

1. Run `install.sh`:

        ./install.sh

    That's it.

### Windows

Follow the directions in the "Installing" sections found below.

## Application

### Installing
1.  Create a virtualenv

2.  Run:

        pip -r install requirements.txt

    to install the necessary packages.

3.  Run:

        python database.py create

    to create the dabase, and

        python database.py migrate

    to migrate the model schema into the database.

### Documentation
Documentation is
[available on readthedocs](http://wordseer-flask.readthedocs.org). You can also
build it yourself:

	cd docs/
	make html

Or, on windows, simply run `make.bat`.

## Pipeline

### Installing
1. `corenlp` must be installed manually. Clone the repository:

        git clone https://github.com/silverasm/stanford-corenlp-python.git
        cd stanford-corenlp-python

    Create a file called `setup.py` in its root directory containing the
    following:

        from setuptools import setup, find_packages
        setup(name='corenlp',
            version='1.0',
            packages=find_packages(),
            package_data = {"": ["*.properties"],
            "corenlp": ["*.properties"]},)

    Then, from the root directory of `corenlp`, execute the following:

        python setup.py install

    This should install `corenlp` to your system.

    In order to complete the setup, version *3.2.0* of Stanford's CoreNLP
    library must simply be in a directory accessible to the backend. From the
    root directory of `wordseerbackend`:

        wget http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip
        unzip stanford-corenlp-full-2013-06-20.zip
        mv stanford-corenlp-full-2013-06-20 stanford-corenlp

2. After installing the above dependencies, make sure you edit
`lib/wordseerbackend/wordseerbackend/config.py` for your setup. Particularly
make sure to point `CORE_NLP_DIR` to the Stanford NLP library. You should then
be ready to parse files. Example XML and JSON files are included in
`tests/data`.

### Documentation
Documentation is
[available on readthedocs](http://wordseerbackend.readthedocs.org). You can also
build it yourself:

	cd lib/wordseerbackend/docs/
	make html

Or, on windows, simply run `make.bat` in the same directory.

## Testing
1. Simply run `runtests.py`:

        python runtests.py

