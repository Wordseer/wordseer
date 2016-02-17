# How to contribute to Wordseer

We have released this software as is and are no longer officially supporting it; it was part of a research project that is now complete. That said, we hope that people find it useful and take it upon themselves to improve it. While we're not actively developing Wordseer at this point, this GitHub repo is still being monitored and we are happy to respond to inquiries and pull requests.

You may find the information below useful if you want to fork this repo and make some improvements.

## History

WordSeer began with Aditi Muralidharan's PhD research and engineering at UC Berkeley with Prof. Marti Hearst; 
there is a wealth of information on that research available on [the WordSeer website](http://wordseer.berkeley.edu/publications-2/)
that can provide useful background for both technical and non-technical contributions.

## Branching

This repo has two main branches:

- `master`, for stable, production-ready code
- `development`, for recent and unstable code

Feature branches that wish to make a change to the application should be
branched from `development`. Once they are ready, they'll be merged into
`development`, which is periodically merged into `master` once it is stable.

Hotfixes that should be applied quickly to `master` are branched off of `master`
and called `hotfix-xyz`. Unit tests must be passing in a hotfix branch before
it can be merged.

Unit tests must always be passing in `master`.

## Ways to contribute

1. [Report bugs](https://github.com/Wordseer/wordseer/issues/new)

2. Fix bugs - we have a conveniently organized
[system](https://waffle.io/Wordseer/wordseer) for contributors to see
what's ready to be [worked on](https://github.com/Wordseer/wordseer/issues?q=is%3Aopen+is%3Aissue+label%3Aready).
Once you've fixed something, you can create a pull request.

## Documentation
Documentation is
[available on readthedocs](http://wordseer.readthedocs.org). You can also
build it yourself:

	cd docs/
	make html

Or, on windows, simply run `make.bat` in the same directory.

## Testing
Simply run `runtests.py`:

    python runtests.py

## Version history

Up through versions 3.X, Wordseer was a collection of PHP/MySQL and JavaScript 
applications. This repository initiates version 4, which is a reimplementation of WordSeer's
PHP components in Python/SQLite that can be run on local machines without requiring
a web server setup. There are two primary components to this new codebase:

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
