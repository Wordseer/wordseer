"""Config for the WordSeer website.
"""
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
APP_NAME = os.path.basename(ROOT)
DEBUG = True
PROPAGATE_EXCEPTIONS = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(ROOT, APP_NAME + ".db")

RELATIONS = {("none",): "search",
    ("",): "(any relation)",
    ("amod", "advmod",): "described as",
    ("agent", "subj", "nsubj", "csubj", "nsubjpass", "csubjpass",): "done by",
    ("obj", "dobj", "iobj", "pobj",): "done to",
    ("prep_because", "prep_because_of", "prep_on_account_of", "prep_owing_to"
        "prepc_because", "prepc_because_of", "prepc_on_account_of",
        "prepc_owing_to",): "because",
    ("conj_and",): "and",
    ("purpcl",): "in order to",
    ("prep_with", "prepc_with", "prep_by_means_of",
        "prepc_by_means_of",): "with",
    ("prep_to",): "to",
    ("prep_from",): "from",
    ("prep_of",): "of",
    ("prep_to",): "to",
    ("prop_from",): "from",
    ("prep_of",): "of",
    ("prep_on",): "on",
    ("prep_by",): "by",
    ("prep_in",): "in",
    ("poss",): "possessed by",
    }

#TODO: unify these options with the pipeline

STOPWORDS = (u"'ve ’s ’ 're does o t went was is had be were did are have "
    "do has being am 's been go 'm the and so are for be but this what 's did "
    "had they doth a to is that was as are at an of with . , ; ? ' \" : "
    "`").split();

PUNCTUATION = list(u"!@#$%^&*()_+-=~`,./;;\"'{}[]|’\\");
