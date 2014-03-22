py_wordseerbackend
==================

This is intended to implement the functionality of
[wordseerbackend](https://bitbucket.org/silverasm/wordseerbackend/overview) into 
more maintainable python.

Requires
--------
* [sqlaclchemy](http://www.sqlalchemy.org/)
* [corenlp](https://github.com/silverasm/stanford-corenlp-python)
* [lxml](http://lxml.de/)
* [Stanford CoreNLP](http://nlp.stanford.edu/software/corenlp.shtml)

Installation
------------

To install `sqlalchemy` and `lxml`:

`pip install SQLAlchemy lxml`

`corenlp` must be installed manually, and Stanford's CoreNLP library must simply
be in a directory accessible to the backend.

Use
---

After installing the above dependencies, make sure you edit the config file
for your setup. Particularly make sure to point `CORE_NLP_DIR` to the Stanford
NLP library.
