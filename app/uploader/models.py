"""

===========
Data Models
===========

This module contains the model-level logic, built on SQLAlchemy.

"""

from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from sqlalchemy.ext.declarative import declared_attr

from app import db

#from config import *

class Base(object):
    """This is a mixin to add to Flask-SQLAlchemy's db.Model class.
    """

    # Define the primary key
    id = db.Column(db.Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def save(self):
        """Commits this model instance to the database

        TODO: should return either True or False depending on its success.
        TODO: manage sequential saves better.

        """
        db.session.add(self)
        db.session.commit()

"""
######
Models
######
"""

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
      belongs to: parent (Unit)
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

        return " ".join([self.unit_type, str(self.number)])

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
      has many: words

    NOTE: should test sentence reconstruction using the actual word model.

    """

    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    text = db.Column(db.Text, index = True)

    words = db.relationship("Word", secondary="word_in_sentence",
        backref=db.backref('sentences', lazy="dynamic")
    )

    def __repr__(self):
        return "<Sentence: " + self.text + ">"

class Word(db.Model, Base):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
      word (str): the word

    Relationships:
      has many: sentences

    """

    word = db.Column(db.String, index = True)

    def __repr__(self):
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

    user = db.Column(db.Integer)
    name = db.Column(db.String)
    files = db.relationship("Unit", backref='project')
    path = db.Column(db.String)

    def __repr__(self):
        return "<Project (name=" + self.name + ")>"

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, Base, RoleMixin):
    """Represents a flask-security user role.
    """
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, Base, UserMixin):
    """Represents a flask-security user.
    """
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

"""
##################
Association Tables
##################
"""

# Many-to-many table between words and sentences
word_in_sentence = db.Table("word_in_sentence",
    db.Column('word_id', db.Integer, db.ForeignKey('word.id')),
    db.Column('sentence_id', db.Integer, db.ForeignKey('sentence.id'))
)
