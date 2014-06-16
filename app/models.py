"""
Models for the wordseer frontend as a whole.

These models set up user authentication, which is used by all blueprints in
the application.
"""

from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
import re

from app import db

class Base(object):
    """This is a mixin to add to Flask-SQLAlchemy"s db.Model class.
    """

    # Define the primary key
    id = db.Column(db.Integer, primary_key=True)

    def save(self):
        """Commits this model instance to the database

        TODO: should return either True or False depending on its success.
        TODO: manage sequential saves better.

        """
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_or_create(cls, **kwargs):
        """Retrieves a record that matches the query, or create a new record
        with the parameters of the query.

        Returns False if more than one record is retrieved.
        """

        match = cls.query.filter_by(**kwargs)

        if match.count() == 0:
            new_record = cls(**kwargs)
            new_record.save()
            return new_record

        elif match.count() == 1:
            return match.first()

        else:
            return False

    def __repr__(self):
        """Default representation string for models.
        """

        repr_str = "<" + self.__class__.__name__ + ":"
        for (k, v) in self.__dict__.items():
            if k[0] != '_':
                repr_str += " | " + str(k) + ": " + str(v)

        repr_str += " |>"

        return repr_str

"""
######
Models
######
"""

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    """Represents a flask-security user role.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    """Represents a flask-security user.
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'))

    sets = db.relationship("Set", backref="user")


class Collection(db.Model, Base):
    """A collection of documents.

    Attributes:

    :keyword str name: The name of the collection

    Relationships:

    :keyword str documents: The documents that belong to this
    """

    name = db.Column(db.String)

    def __init__(self, name = ""):
        """Initialize the collection with a name.
        """

        self.name = name

class Document(db.Model, Base):
    """A model for a single document file.

    Documents are top-level Units. See the description in the Unit model for
    further details.

    Attributes:
      title (str): the title of the document
      path (str): the location of the file on the system
      unit_id (int): a link to its corresponding unit
      collection_id (int): a link to its collection

    Relationships:
      has one: unit
      has many: sentences
      belongs to: collection
    """

    # Attributes

    title = db.Column(db.String, index = True)
    path = db.Column(db.String)
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    sentence_count = db.Column(db.Integer)

    # Relationships

    sentences = db.relationship("Sentence", backref="document")
    unit = db.relationship("Unit", backref="document")
    collection = db.relationship("Collection", backref="document")

    def __init__(self, title = "", path = ""):
        """Initialize a document, which also creates the corresponding unit.
        """

        self.title = title
        self.path = path

        unit = Unit()
        unit.unit_type = "document"
        self.unit = unit

    @property
    def properties(self):
        """Convenience access to this document's properties
        """

        return self.unit.properties

    @property
    def children(self):
        """Convenience access for its immediate children
        """

        return self.unit.children

    def __repr__(self):
        return "<Document: " + self.title + ">"

class Unit(db.Model, Base):
    """A model representing a unit (or segment) of text.

    This can be either a section or chapter of a document, an act in a play, or
    anything that is made of sentences.

    Units are hierarchical; one unit can contain many children units.

    Attributes:
      unit_type (str): the unit type (document, section, etc.).
      number (int): a sequencing number (e.g. 2 for chapter 2).
      parent_id (int): a link to the parent unit.

    Relationships:
      has one: document
      has many: children (Unit), sentences, properties
    """

    # Attributes

    unit_type = db.Column(db.String(64), index = True)
    number = db.Column(db.Integer, index = True)
    parent_id = db.Column(db.Integer, db.ForeignKey("unit.id"))

    # Relationships

    children = db.relationship("Unit")
    sentences = db.relationship("Sentence", backref="unit")
    properties = db.relationship("Property", backref="unit")

    def __init__(self, unit_type="", number=0):
        """Default constructor for units, setting its type and number.
        """

        self.unit_type = unit_type
        self.number = number


    @property
    def parent(self):
        """Method for getting a unit's parent.

        This method exists because in the current set up, it has been tricky to
        define the parent as a db.relationship.
        """

        return Unit.query.get(self.parent_id)

    @classmethod
    def documents(cls):
        """Returns units of the document type.

        Note that this should eventually take a collection as a parameter, or
        be replaced by a method from the Collection model
        """

        return Unit.query.filter_by(unit_type="document").all()

    def __repr__(self):
        """Return a representation of a unit, which is its type followed by its
        ordering number
        """

        return "<Unit: " + " ".join([str(self.unit_type), str(self.number)]) + ">"

class Sentence(db.Model, Base):
    """A model representing a sentence.

    The sentence model is treated like "leaf" units. It has a link to its
    parent unit as well as the top-level document. Sentences contain words
    (the model), and also stores its own raw text, for use in search results.

    Attributes:
      unit_id: a link to the unit containing the sentence.
      document_id: the document (top-level unit) to which this sentence belongs to.
      text: the raw text of the sentence.

    Relationships:
      belongs to: unit, document
      has many: words, sequences, dependencies
    """

    # Attributes

    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    document_id = db.Column(db.Integer, db.ForeignKey("document.id"))
    text = db.Column(db.Text, index = True)

    # Relationships

    words = association_proxy("word_in_sentence", "word")
    sequences = association_proxy("sequence_in_sentence", "sequence")
    dependencies = association_proxy("dependency_in_sentence", "dependency")

    def __init__(self, text=""):
        """Initialize the sentence with the text of the sentence.
        """

        self.text = text

    def __repr__(self):
        """Representation of the sentence, showing its text.

        NOTE: could be trucated to save print space
        """

        return "<Sentence: " + self.text + ">"

    @property
    def tagged(self):
        """Temporary compatibility method
        """

        return self.words

    def add_word(self, word, position=None, space_before="", tag=""):
        """Add a word to the sentence by explicitly creating the association
        object.

        """

        word_in_sentence = WordInSentence(
            word = word,
            sentence = self,
            position = position,
            space_before = space_before,
            tag = tag
        )
        word_in_sentence.save()

        return word_in_sentence

    def add_dependency(self, dependency, governor_index=None,
        dependent_index=None):
        """Add a dependency to the sentence by explicitly creating the
        association object.
        """

        dependency_in_sentence = DependencyInSentence(
            dependency = dependency,
            sentence = self,
            governor_index = governor_index,
            dependent_index = dependent_index
        )

        dependency_in_sentence.save()

        return dependency_in_sentence

    def add_sequence(self, sequence, position=None):
        """Add a sequence to the sentence by explicitly creating the
        association object.
        """

        sequence_in_sentence = SequenceInSentence(
            sequence = sequence,
            sentence = self,
            position = position
        )

class Word(db.Model, Base):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
      word (str): the word

    Relationships:
      has many: sentences
    """

    # Attributes

    word = db.Column(db.String, index = True)
    lemma = db.Column(db.String, index = True)
    tag = db.Column(db.String, index = True)

    # Relationships

    sentences = association_proxy("word_in_sentence", "sentence")

    def __init(self, word = "", lemma = "", tag = ""):
        """Initialize a word with its word, lemma, and tag.
        """

        self.word = word
        self.lemma = lemma
        self.tag = tag

    def __repr__(self):
        """Representation string for words, showing the word.
        """

        return "<Word: " + self.word + ">"

class Property(db.Model, Base):
    """A model representing a property of a unit.

    Metadata about units are stored as properties, which have a link to the
    unit it belongs to. Any form of metadata can be assigned to a unit, making
    them extensible and flexible.

    Attributes:
      unit_id: the primary key of the unit it belongs to
      name: the name of the property
      value: the value of the property

    Relationships:
      belongs to: unit

    """

    # Attributes
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"))
    name = db.Column(db.String, index = True)
    value = db.Column(db.String, index = True)

    def __init__(self, name="", value=""):
        """Initialize the property with a name and value
        """

        self.name = name
        self.value = value

    def __repr__(self):
        """Representation string for properties, showing the property name
        """

        return "<Property: " + self.name + ">"

class Sequence(db.Model, Base):
    """A sequence of at most 4 consecutive words in a sentence.

    Some sequences are lemmatized and are not the same as they appear in the
    original sentence.

    Attributes:
      sequence (str): the sequence text
      lemmatized (bool): whether or not it is lemmatized
      has_function_words (bool): whether or not it has function words
      all_function_words (bool): whether or not it is made of all function words
      length (int): the length of the sequence
      sentence_count (int): the number of sentences this sequence appears in
      document_count (int): the number of documents this sequence appears in

    Relationships:
      belongs to: sentence
    """

    # Attributes

    sequence = db.Column(db.String, index = True)
    lemmatized = db.Column(db.Boolean)
    has_function_words = db.Column(db.Boolean)
    all_function_words = db.Column(db.Boolean)
    length = db.Column(db.Integer, index = True)
    sentence_count = db.Column(db.Integer, index = True)
    document_count = db.Column(db.Integer, index = True)

    # Relationships

    sentences = association_proxy("sequence_in_sentence", "sentence")

    def __init__(self, sequence=None, lemmatized=False, has_function_words=False,
        all_function_words=False, length=None):
        """Initialize a sequence with all necessary fields
        """

        self.sequence = sequence
        self.lemmatized = lemmatized
        self.has_function_words = has_function_words
        self.all_function_words = all_function_words
        self.length = length

class GrammaticalRelationship(db.Model, Base):
    """A grammatical relationship between two words.

    This indicates the type of relationship between the governor and the
    dependent in the dependency model.

    Attributes:
      name (str): the name of the relationship

    Relationships:
      belongs to: dependency
    """

    # Attributes

    name = db.Column(db.String, index = True)

    def __init__(self, name):
        """Initialize with the name of the relationship
        """
        self.name = name

class Dependency(db.Model, Base):
    """A representation of the grammatical dependency between two words.

    Each dependency is comprised of a governor, a dependent, and a grammatical
    relationship.

    Attributes:
      grammatical_relationship_id (int): link to the grammatical relationship
      governor_id (int): link to the governor word
      dependent_id (int): link to the dependent word
      sentence_count (int): the number of sentences this appears in
      document_count (int): the number of documents this appears in

    Relationships:
      has one: dependent (Word), governor (Word), grammatical relationship
      has many: sentences
    """

    # Attributes

    grammatical_relationship_id = db.Column(
        db.Integer, db.ForeignKey("grammatical_relationship.id")
    )
    governor_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    dependent_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sentence_count = db.Column(db.Integer, index = True)
    document_count = db.Column(db.Integer, index = True)

    # Relationships

    grammatical_relationship = db.relationship(
        "GrammaticalRelationship", backref="dependency"
    )
    governor = db.relationship(
        "Word", foreign_keys = [governor_id], backref = "governor_dependencies"
    )
    dependent = db.relationship(
        "Word", foreign_keys = [dependent_id], backref = "dependent_dependencies"
    )

    sentences = association_proxy("dependency_in_sentence", "sentence")

    def __init__(self, relationship, governor, dependent):
        """Create a dependency between the governor and dependent with the given
        grammatical relationship
        """

        self.grammatical_relationship = relationship
        self.governor = governor
        self.dependent = dependent

    def __repr__(self):
        """Representation string for the dependency
        """

        rel = self.grammatical_relationship.relationship
        gov = self.governor.word
        dep = self.dependent.word

        return "<Dependency: " + rel + "(" + gov + ", " + dep + ") >"

"""
##################
Association Tables
##################
"""

class WordInSentence(db.Model, Base):
    """Association object for words in sentences
    """

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    position = db.Column(db.Integer)
    space_before = db.Column(db.String)
    tag = db.Column(db.String)

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "word_in_sentence", cascade="all, delete-orphan"
        )
    )

    word = db.relationship("Word",
        backref=db.backref(
            "word_in_sentence", cascade="all, delete-orphan"
        )
    )

    def __init__(self, word=None, sentence=None, position=None, space_before="",
        tag=""):

        self.word = word
        self.sentence = sentence
        self.position = position
        self.space_before = space_before
        self.tag = tag

class SequenceInSentence(db.Model, Base):
    """Association object for sequences in sentences
    """

    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    position = db.Column(db.Integer)

    sequence = db.relationship("Sequence",
        backref=db.backref(
            "sequence_in_sentence", cascade="all, delete-orphan"
        )
    )

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "sequence_in_sentence", cascade="all, delete-orphan"
        )
    )

    def __init__(self, sequence=None, sentence=None, position=None):
        self.sequence = sequence
        self.sentence = sentence
        self.position = position

class DependencyInSentence(db.Model, Base):
    """Association object for dependencies in sentences
    """

    dependency_id = db.Column(db.Integer, db.ForeignKey("dependency.id"))
    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"))
    governor_index = db.Column(db.Integer)
    dependent_index = db.Column(db.Integer)

    dependency = db.relationship("Dependency",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"
        )
    )

    sentence = db.relationship("Sentence",
        backref=db.backref(
            "dependency_in_sentence", cascade="all, delete-orphan"
        )
    )

    def __init__(self, dependency=None, sentence=None, governor_index=None,
        dependent_index=None):

        self.dependency = dependency
        self.sentence = sentence
        self.governor_index = governor_index
        self.dependent_index = dependent_index
