wordseerbackend
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

    pip install SQLAlchemy lxml Unidecode

If you want to run unit tests, you should install `mock`:

    pip install mock

Or, you can simply use the `requirements.txt` file:

    pip install -r requirements.txt

`corenlp` must be installed manually. Clone the repository:

    git clone https://github.com/silverasm/stanford-corenlp-python.git
    cd stanford-corenlp-python

Create a file called `setup.py` in its root directory containing the
following:

    from setuptools import setup, find_packages
    setup(name='corenlp',
          version='1.0',
          packages=find_packages(),
          package_data = {"": ["*.properties"],
                "corenlp": ["*.properties"]},
          )

Then, from the root directory of `corenlp`, execute the following:

    python setup.py install

This should install `corenlp` to your system.

In order to complete the setup, version *3.2.0* of Stanford's CoreNLP
library must simply be in a directory accessible to the backend. From the
root directory of `wordseerbackend`:

    wget http://nlp.stanford.edu/software/stanford-corenlp-full-2013-06-20.zip
    unzip stanford-corenlp-full-2013-06-20.zip
    mv stanford-corenlp-full-2013-06-20 stanford-corenlp

You must also run the `createdb.py` script before running for the first time:

    python createdb.py

Use
---

After installing the above dependencies, make sure you edit the config file
for your setup. Particularly make sure to point `CORE_NLP_DIR` to the Stanford
NLP library. You should then be ready to parse files. Example XML and JSON
files are included in `tests/data`.

Testing
-------

To run all tests, simply run `runtests.py` from the root directory.
Alternatively, use the following syntax to run only one module's tests.

    python -m unittest -v tests.testdesiredmodule

Documentation
-------------

Documentation is available 
[on readthedocs](http://wordseerbackend.readthedocs.org/en/latest/).
If you want to build the documentation, you will need to install `sphinx`:

    pip install sphinx

Then run `make html` in the `docs` directory.

