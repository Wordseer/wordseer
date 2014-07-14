"""The ``Base`` class that provides some helpful methods to other models.
"""
import re

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from app import db

class Base(object):
    """This is a mixin to add to Flask-SQLAlchemy"s db.Model class.

    Attributes:
        id (int): the primary key for all models
        holds (dict): a dictionary that maps model class names to a set of
            instances of that model. Used for mass-commits to avoid commit
            overhead.
    """

    # Define the primary key
    id = db.Column(db.Integer, primary_key=True)

    # Flag for commit on save
    commit_on_save = False

    @declared_attr
    def __tablename__(cls):
        """Convert camel case class name to snake for the tables.

        Although db.Model should include a __tablename__ by default, the mixin
        does not seem to be working as expected; hence, we have left this
        method here that works the same as flask_sqlalchemy's.
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def save(self, force=False):
        """Commits this model instance to the database
        """

        db.session.add(self)

        if Base.commit_on_save or force:
            db.session.commit()

    def delete(self):
        """Deletes this model instance and commits.
        """

        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_or_create(cls, **kwargs):
        """Retrieves a record that matches the query, or create a new record
        with the parameters of the query.

        Arguments:
            kwargs: Conditions that the record should match.

        Returns:
            ``False`` if more than one record is retrieved, a new instance
            of the model if none are found, and the existing instance if one
            is found.
        """

        try:
            match = cls.query.filter_by(**kwargs).one()
        except NoResultFound:
            new_record = cls(**kwargs)
            new_record.save(force=True)
            return new_record
        except MultipleResultsFound:
            return False

        return match

    @classmethod
    def find_or_initialize(cls, **kwargs):
        """Retrieves a record that matches the query, or initialize a new record
        with the parameters of the query.

        Arguments:
            kwargs: Conditions that the record should match.

        Returns:
            ``False`` if more than one record is retrieved, a new instance
            of the model if none are found, and the existing instance if one
            is found.
        """

        try:
            match = cls.query.filter_by(**kwargs).one()
        except NoResultFound:
            new_record = cls(**kwargs)
            return new_record
        except MultipleResultsFound:
            return False

        return match

    def __repr__(self):
        """Default representation string for models.

        Output format is as follows::

            <ClassName: | att1: val1 | att2: val2 | .... |>
        """

        repr_str = "<" + self.__class__.__name__ + ":"
        for (k, v) in self.__dict__.items():
            if k[0] != '_':
                repr_str += " | " + str(k) + ": " + str(v)

        repr_str += " |>"

        return repr_str

