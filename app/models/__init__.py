from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import create_engine, Column, Integer
from config import *
from sqlalchemy.orm import sessionmaker

# create database connection
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# defined models
__all__ = [
    "unit",
    "document",
    "word",
    "sentence",
    "metadata",
    "association_tables",
]

# custom base model
class Base(object):

    @declared_attr
    def __tablename__(cls):

        # table name should be plural of model name
        return cls.__name__.lower()

    id =  Column(Integer, primary_key=True)

    # Commits this model instance to the database
    def save(self):
        session.add(self)
        session.commit()

    # Look up with id
    @staticmethod
    def find(id):
        return session.query(cls).filter(cls.id==id)

Base = declarative_base(cls=Base)
