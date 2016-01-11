from .association_objects import SentenceInQuery
from .base import Base
from .sentence import Sentence

from app import db
from sqlalchemy.ext.associationproxy import association_proxy

class Query(db.Model, Base):
    """A model to store queries, used in concert with SentenceInQuery to
    implement sentence caching.
    """

    # Attributes
    project_id = db.Column(db.Integer, db.ForeignKey("project.id", ondelete='CASCADE'))
    
    # Relationship
    project = db.relationship("Project")
    sentences = association_proxy("sentence_in_query", "sentence",
        creator=lambda sentence: SentenceInQuery(sentence=sentence))

    @staticmethod
    def is_grammatical_search_query(search_query_dict):
    	""" Checks the search query parameters and determines whether the
    	query is a grammatical search query.

    	Arguments:
    		search_query_dict (dict): A dictionary representation of a search
    			query. Contains the keys:
    				- gov: The governor word in the case of grammatical search
    					or the string search query in the case of a
    					non-grammatical search. 
    				- dep: The dependent word in the case of grammatical search
    				    (ignored for a non-grammatical search)
    				- relation: The grammatical relationships. A space-separated
    					list of grammatical relationship identifiers. If this
    					is "" or not present, the search is assumed to be
    					non-grammatical.
    	"""
    	if 'relation' in search_query_dict:
    		return search_query_dict['relation'] != ""
    	return False
