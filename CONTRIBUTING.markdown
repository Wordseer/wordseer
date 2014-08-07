# How to contribute to Wordseer

If you'd like to contribute, we'll be happy to have your help. Here's an
overview of our development process.

## Branching

We have two main branches:

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

1. [Report bugs](https://github.com/Wordseer/wordseer_flask/issues/new)

2. Fix bugs - we have a conveniently organized
[system](https://waffle.io/wordseer/wordseer_flask) for contributors to see
what's ready to be [worked on](https://github.com/Wordseer/wordseer_flask/issues?q=is%3Aopen+is%3Aissue+label%3Aready).
Once you've fixed something, you can create a pull request.

