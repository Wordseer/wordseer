from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import create_engine, Column, Table, Integer, String, Boolean, ForeignKey, Text
from config import *
from sqlalchemy.orm import relationship, backref, sessionmaker

# create database connection
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# custom base model
class Base(object):

    @declared_attr
    def __tablename__(cls):

        # table name should be plural of model name
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)

    # Commits this model instance to the database
    def save(self):
        session.add(self)
        session.commit()

    # Look up with id
    @classmethod
    def get(cls, id):
        return session.query(cls).filter(cls.id==id).first()

    # Get all records
    @classmethod
    def all(cls):
        return session.query(cls)

    # Criteria-based look-up; see SQLAlchemy docs for use
    @classmethod
    def filter(cls, criteria):
        return session.query(cls).filter(criteria)

Base = declarative_base(cls=Base)

class Unit(Base):
    unit_type = Column(String(64), index = True)
    number = Column(Integer, index = True)

class Sentence(Base):

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    text = Column(Text, index = True)

    # Relationships
    unit = relationship("Unit", backref=backref("sentences"))

    words = relationship("Word",
        secondary="word_in_sentence",
        backref="sentences"
    )

class Word(Base):

    # Schema
    word = Column(String, index = True)

class Metadata(Base):

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    property_name = Column(String, index = True)
    property_value = Column(String, index = True)

    # Relationships
    unit = relationship("Unit", backref=backref("metadata", uselist=False))

# Many-to-many table between this model and the Word model
word_in_sentence = Table("word_in_sentence", Base.metadata,
    Column('word_id', Integer, ForeignKey('word.id')),
    Column('sentence_id', Integer, ForeignKey('sentence.id'))
)
