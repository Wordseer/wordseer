from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import create_engine, Column, Integer
from config import *
from sqlalchemy.orm import sessionmaker

# create database connection
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()# defined models
__all__ = ["unit", "document"]

# custom base model
class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'InnoDB'}

    id =  Column(Integer, primary_key=True)

    # Commits this model instance to the database
    def save(self):
        session.add(self)
        session.commit()

Base = declarative_base(cls=Base)
