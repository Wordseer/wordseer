"""
Data models for the uploader.

This module contains the model-level logic specific to the uploader blueprint,
built on SQLAlchemy.
"""

from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from app.models import Base

# Models
class Unit(db.Model, Base):
    """A model representing a unit (or segment) of text.

    This can be either a full document, a section or chapter of a document,
    an act in a play, or anything that is made of sentences.

    Units are hierarchical; one unit can contain many children units.

    Attributes:
      unit_type (str): the unit type (document, section, etc.).
      number (int): a sequencing number (e.g. 2 for chapter 2).
      parent_id (int): a link to the parent unit.
      path (str): The path to this unit, if it exists as a file.

    Relationships:
      belongs to: parent (Unit), set (DocumentSet)
      has many: children (Unit), sentences, properties

    TODO: implement db.relationships

    """

    unit_type = db.Column(db.String(64), index = True)
    number = db.Column(db.Integer, index = True)
    parent_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    path = db.Column(db.String, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    # Relationships

    children = db.relationship("Unit")
    sentences = db.relationship("Sentence", backref='unit')
    properties = db.relationship("Property", backref='unit')

    def __init__(self, document=None, **kwargs):
        """Initialize a top-level document unit from a document file.

        Expects a dictionary that has the following entries:
        - properties (dict): the metadata of the document
        - subunits (dict): the structure of the subunits
        - sentences (list): a list of sentences, in order
        - words (set): the set of all words (or tokens)

        This is tentative.

        The problem with this sort of constructor is that it's difficult
        to pass in the other types of values (the columns for this table).
        I think adding a kwargs argument will make things better - David

        """
        if document:
            self.unit_type = "document"
            self.number = 0

            for name, value in document["properties"].items():
                prop = Property()
                prop.name = name
                prop.value = value

                prop.save()
                self.properties.append(prop)

            for sentence_tuple in document["sentences"]:
                words = sentence_tuple[1]
                sentence_text = sentence_tuple[0]

                sentence = Sentence()
                sentence.text = sentence_text

                for word_str in words:
                    word = Word()
                    word.word = word_str
                    word.save()

                    sentence.words.append(word)

                sentence.save()
                self.sentences.append(sentence)

            # TODO: initialize subunits
            self.save

        super(Unit, self).__init__(**kwargs)

    @property
    def parent(self):
        """Method for getting a unit's parent.

        This method exists because in the current set up, it has been tricky to
        define the parent as a db.relationship.
        """

        return Unit.query.get(self.parent_id)

    def __repr__(self):
        """Return a representation of a unit, which is its type followed by its
        ordering number.
        """

        return str(self.unit_type) + " " + str(self.number)

class Sentence(db.Model, Base):
    """A model representing a sentence.

    The sentence model is treated like "leaf" units. It has a link to its
    parent unit. Sentences contain words (the model), and also stores its
    own raw text, for use in search results.

    Attributes:
      unit_id: a link to the unit containing the sentence.
      text: the raw text of the sentence.

    Relationships:
      belongs to: unit
      belongs to: sentenceset
      has many: words

    NOTE: should test sentence reconstruction using the actual word model.

    """

    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    text = db.Column(db.Text, index = True)

    sentence_words = db.relationship("WordInSentence")
    words = association_proxy("sentence_words", "word",
        creator=lambda word: WordInSentence(word=word))

    sentence_dependencies = db.relationship("DependencyInSentence")
    dependencies = association_proxy("sentence_dependencies", "dependency",
        creator=lambda dep: DependencyInSentence(dependency=dep))

    sentence_sequences = db.relationship("SequenceInSentence")
    sequences = association_proxy("sentence_sequences", "sequence",
        creator=lambda seq: SequenceInSentence(sequence=seq))

    def __repr__(self):
        return "<Sentence: " + str(self.text) + ">"

class Word(db.Model, Base):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
      word (str): The word.
      tag (str): The part of speech of the word.

    Relationships:
      has many: sentences

    """

    word = db.Column(db.String, index = True)
    lemma = db.Column(db.String)

    word_sentences = db.relationship("WordInSentence")
    sentences = association_proxy("word_sentences", "sentence",
        creator=lambda sent: WordInSentence(sentence=sent))

    def __repr__(self):
        return "<Word: " + str(self.word) + ">"

class Sequence(db.Model, Base):
    """A Sequence is a series of words.
    """

    sequence_sentences = db.relationship("SequenceInSentence")
    sentences = association_proxy("sequence_sentences", "sentence",
        creator=lambda sent: SequenceInSentence(sentence=sent))

    sequence = db.Column(db.String)
    is_lemmatized = db.Column(db.Boolean)
    all_function_words = db.Column(db.Boolean)
    length = db.Column(db.Integer)
    words = db.relationship("Word", secondary="word_in_sequence")

class Dependency(db.Model, Base):
    """Just a placeholder.
    """

    relationship = db.Column(db.String)
    governor = db.Column(db.String)
    gov_index = db.Column(db.Integer)
    dependent = db.Column(db.String)
    dep_index = db.Column(db.Integer)

    dependency_sentences = db.relationship("DependencyInSentence")
    sentences = association_proxy("dependency_sentences", "sentence",
        creator=lambda sen: DependencyInSentence(sentence=sen))

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

    # Schema
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    name = db.Column(db.String, index = True)
    value = db.Column(db.String, index = True)

    def __repr__(self):
        return "<Property: " + self.name + ">"

class Project(db.Model, Base):
    """A model representing a project.

    Projects are collections of associated files, grouped together for the
    user's convenience.
    """

    user = db.Column(db.Integer) #TODO: not a real relationship
    name = db.Column(db.String)
    files = db.relationship("Unit", backref='project')
    path = db.Column(db.String)

    def __repr__(self):
        return "<Project (name=" + self.name + ")>"

# Association tables
class WordInSentence(db.Model):
    """Describes a single Word in a single Sentence.

    A Word in a Sentence has special attributes unique to one specific
    ocurrence, described below.

    Attributes:
        word_id (int): The ID of the Word that this object describes.
        sentence_id (int): The ID of the Sentence that this object describes.
        space_before (str): If there is a space after this Word, then there
            is a space character here. Otherwise, it is empty.
        tag (str): The part of speech of this Word in this Sentence.
        position (int): The position (0-indexed) of the Word in the Sentence.
    """

    word_id = db.Column(db.Integer, db.ForeignKey('word.id'),
        primary_key=True)
    sentence_id = db.Column(db.Integer, db.ForeignKey('sentence.id'),
        primary_key=True)
    space_before = db.Column(db.String)
    tag = db.Column(db.String)
    position = db.Column(db.Integer)

    word = db.relationship("Word")
    sentence = db.relationship("Sentence")

class DependencyInSentence(db.Model):
    """Describes a Dependency in a Sentence.

    Since a Dependency always has the same two Words but may appear in
    different Sentences, it is necessary to describe the positions of the
    governor and the dependent on a case-by-case basis.

    Attributes:
        dependency_id (int): The ID of the Dependency in this relationship.
        sentence_id (int): The ID of the Sentence in this relationship.
        gov_id (int): The position (0-indexed) of the governor in this
            relationship.
        dep_id (int): The position (0-indexed) of the dependency in this
            relationship.
    """
    dependency_id = db.Column(db.Integer, db.ForeignKey("dependency.id"),
        primary_key=True)

    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"),
        primary_key=True)

    sentence = db.relationship("Sentence")
    dependency = db.relationship("Dependency")

    gov_index = db.Column(db.Integer)
    dep_index = db.Column(db.Integer)

class SequenceInSentence(db.Model):
    """Describes a relationship between a Sequence and a Sentence.

    Attributes:
        sequence_id (int): The ID of the Sequence in this relationship.
        sentence_id (int): The ID of the Sentence in this relationship.
        sequence_capitalization (str): A string with the exact capitalization
            of this sequence in this sentence.
        start_index (int): The position (0-indexed) of the first word of this
            Sequence in this sentence.
    """

    sequence_id = db.Column(db.Integer, db.ForeignKey("sequence.id"),
        primary_key=True)

    sentence_id = db.Column(db.Integer, db.ForeignKey("sentence.id"),
        primary_key=True)

    sentence = db.relationship("Sentence")
    sequence = db.relationship("Sequence")

    sequence_capitalization = db.Column(db.String)
    start_index = db.Column(db.Integer)

word_in_sequence = db.Table("word_in_sequence",
    db.Column("word_id", db.Integer, db.ForeignKey("word.id")),
    db.Column("sequence_id", db.Integer, db.ForeignKey("sequence.id"))
)

