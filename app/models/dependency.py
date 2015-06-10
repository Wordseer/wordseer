from .counts import DependencyCount
from .association_objects import DependencyInSentence
from .grammaticalrelationship import GrammaticalRelationship
from .project import Project
from .sentence import Sentence
from .word import Word
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from base import Base

class Dependency(db.Model, Base):
    """A representation of the grammatical dependency between two words.

    Each dependency is comprised of a governor, a dependent, and a grammatical
    relationship.

    Attributes:
        grammatical_relationship (GrammaticalRelationship): The
            ``GrammaticalRelationship`` which describes the relationship between
            the governor and the dependent.
        governor (Word): The governor ``Word``.
        dependent (Word): The dependent ``Word``.
        sentence_count (int): the number of sentences this appears in
        document_count (int): the number of documents this appears in
        sentences (list of Sentences): ``Sentence``\s that this dependency is
            in.

    Relationships:
        Has one: dependent (Word), governor (Word), grammatical relationship
        Has many: sentences
    """

    # Attributes

    grammatical_relationship_id = db.Column(
        db.Integer, db.ForeignKey("grammatical_relationship.id"))
    governor_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    dependent_id = db.Column(db.Integer, db.ForeignKey("word.id"))

    # Relationships

    grammatical_relationship = db.relationship(
        "GrammaticalRelationship", backref="dependencies")

    governor = db.relationship("Word", foreign_keys=[governor_id])

    dependent = db.relationship("Word", foreign_keys=[dependent_id])

    # Scoped Pseudo-relationships

    @property
    def sentences(self):
        """Retrieves all sentences that contain this dependency, within
        the scope of the current active project.
        """

        return Sentence.query.join(DependencyInSentence).join(Dependency).\
            filter(DependencyInSentence.project==Project.active_project).\
            filter(DependencyInSentence.dependency==self).all()

    def get_counts(self, project=None):

        # project argument assigned active_project if not present
        if project == None: project = Project.active_project

        return DependencyCount.fast_find_or_initialize(
            "dependency_id = %s and project_id = %s" % (self.id, project.id),
            dependency_id = self.id, project_id = project.id)

    @staticmethod
    def apply_grammatical_search_filter(search_query_dict, sentence_query):
        """ Gets the sentences that contain the dependency relations specified
        by the query parameters.

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
        Returns:
            A list of Sentence objects that contain the dependencies specified
            by the query parameters.
        """
        
        search_lemmas = "all_word_forms" in search_query_dict and search_query_dict["all_word_forms"] == 'on'
        
        gov_ids = Word.get_matching_word_ids(
                search_query_dict["gov"],
                is_set_id = search_query_dict["govtype"] != "word", search_lemmas=search_lemmas)
        dep_ids = Word.get_matching_word_ids(
                search_query_dict["dep"],
                is_set_id = search_query_dict["deptype"] != "word", search_lemmas=search_lemmas)
        relationship = GrammaticalRelationship.query.filter(
            GrammaticalRelationship.name == search_query_dict["relation"]).first()

        matching_dependencies = Dependency.query;
        if relationship is not None:
            matching_dependencies = matching_dependencies.filter(
                Dependency.grammatical_relationship == relationship)
        if len(gov_ids) > 0:
            matching_dependencies = matching_dependencies.filter(
                Dependency.governor_id.in_(gov_ids))
        if len(dep_ids) > 0:
            matching_dependencies = matching_dependencies.filter(
                Dependency.dependent_id.in_(dep_ids))
        
        matching_dependencies = matching_dependencies.subquery()
        sentence_query = sentence_query.\
            join(DependencyInSentence,
                 DependencyInSentence.sentence_id == Sentence.id).\
            join(matching_dependencies,
                DependencyInSentence.dependency_id ==
                matching_dependencies.c.id)
        return sentence_query

    def __repr__(self):
        """Representation string for the dependency
        """

        #rel = str(self.grammatical_relationship.name)
        #gov = str(self.governor.word)
        #dep = str(self.dependent.word)

        return "<Dependency: " + str(self.grammatical_relationship) + "(" + \
            str(self.governor) + ", " + str(self.dependent) + ") >"

