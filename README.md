py_wordseerbackend
==================

This is intended to implement the functionality of
[wordseerbackend](https://bitbucket.org/silverasm/wordseerbackend/overview) into 
more maintainable python.

Requires
--------
* [SQLAlchemy](http://www.sqlalchemy.org/)
* [corenlp](https://github.com/silverasm/stanford-corenlp-python)
* [lxml](http://lxml.de/)
* [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml):
Specifically version 3.2.0
* [Unidecode](https://pypi.python.org/pypi/Unidecode/)
* [Mock](https://pypi.python.org/pypi/mock) (Only required for unit tests)


Installation
------------

`sqlalchemy`, `lxml`, and `Unidecode` can be installed via `pip`:

`pip install SQLAlchemy lxml Unidecode`

If you want to run unit tests, you should install `mock`:

`pip install mock`

`corenlp` must be installed manually, and version *3.2.0* of Stanford's CoreNLP
library must simply be in a directory accessible to the backend.

You must also run the `createdb.py` script before running for the first time:

`python2.7 createdb.py`

Use
---

After installing the above dependencies, make sure you edit the config file
for your setup. Particularly make sure to point `CORE_NLP_DIR` to the Stanford
NLP library. You should then be ready to parse files. Example files are
included in `tests/data`.

Testing
-------

To test, simply run `runtests.py` from the root directory.