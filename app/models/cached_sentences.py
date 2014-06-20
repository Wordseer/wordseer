from app import db
from base import Base

class CachedSentences(db.Model, Base):
    """Cached list of ``Sentences`` for a query.

    When a ``User`` does a query we pre-compute the set of sentences that
    matches this query so that the 5 default views (of the JavaScript frontend)
    don't all have to compute it separately.

    This model stores the relevant query ID and a list of Sentences.
    The query ID of a given entry is its ID.

    Attributes:
        sentences (list): A list of ``Sentence``s connected with this query.
    """

    sentences = db.relationship("Sentence",
        secondary="sentences_in_queries")
