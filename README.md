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

### Linux/OS X

Run `install.py` like so:

    ./install.py -i

This will launch the interactive installer which will guide you through the
simple installation process.

If you know what you want, run `install.py -h` to view known console flags.

### Windows

Double click on `install.bat` and follow the prompts.

## Use

After installation has completed, you are ready to run WordSeer.

### Linux/OS X

Run `wordseer.py`:

    ./wordseer.py

### Windows

Double click on `wordseer.bat`.

In either case, you will see a console window with an IP address. Navigate
to that address in your browser and you should see the WordSeer welcome
screen.

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

