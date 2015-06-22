"""Set models.
"""
import datetime

from app import db
from .association_objects import SequenceInSentence, PropertyOfSentence
from .base import Base
from .project import Project
from .sequence import Sequence
from .sentence import Sentence
from .document import Document
from .property import Property
from .property_metadata import PropertyMetadata

class Set(db.Model, Base):
    """This is the basic ``Set`` class.

    ``Set``\s contain other objects; by default, there are ``DocumentSet``\s,
    ``SentenceSet``\s, and ``SequenceSet``\s, containing ``Document``\s,
    ``Sentence``\s, and ``Sequence``\s respectively.

    A ``Set`` model has an association with a ``User`` and has some properties
    like a name and a creation date.

    The more specialized type of ``Set``\s (like ``SequenceSet``\s, etc) inherit
    from this class.

    Attributes:
        user (User): The ``User`` that owns this ``Set``
        name (str): The name of this ``Set``
        creation_date (str): A ``date.DateTime`` object of when this ``Set`` was
            created.
        type (str): The type of ``Set`` that this is.
    """

    # Attributes
    # We need to redefine ID to nest sets
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String)
    creation_date = db.Column(db.DateTime)
    type = db.Column(db.String, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("set.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    # Relationships
    children = db.relationship("Set", backref=db.backref("parent",
        remote_side=[id]))

    __mapper_args__ = {
        "polymorphic_identity": "set",
        "polymorphic_on": type,
    }

    def get_items(self):
        """Subclasses of ``Set`` should override this method to return a list
        of whatever they are ``Set``\s of.
        """

        raise NotImplementedError()

    def delete_metadata(self):
        properties = Property.query.filter_by(name = self.type +"_set",
                                              value = self.id).all()
        for property in properties:
            property.delete()
        db.session.commit()

class SequenceSet(Set):
    """A ``Set`` that can have a list of ``Sequences`` in it.

    The ``type`` attribute a ``SequenceSet`` is set to ``sequenceset``.

    Attributes:
        sequences (list): A list of ``Sequence``s in this ``SequenceSet``.
    """

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    sequences = db.relationship("Sequence",
        secondary="sequences_in_sequencesets",
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "phrase",
    }

    def get_items(self):
        """Return the ``Sequence``\s associated with this ``SequenceSet``.

        Returns:
            list of Sequences
        """
        return self.sequences

    def add_items(self, sequences):
        """ Adds the given sequences to this set and adds metadata properties
        for the sentences in which this sequence is found that those sentences
        are in this set."""
        sequences = Sequence.query.filter(Sequence.sequence.in_(sequences))
        self.sequences.extend(sequences)
        self.save()
        sequence_ids = map(lambda s : s.id, sequences)
        matching_sentences = SequenceInSentence.query.filter(
            SequenceInSentence.sequence_id.in_(sequence_ids))
        metadata = PropertyMetadata.query.filter_by(
            property_name = "phrase_set").first()
        property = Property(
            project = self.project,
            property_metadata = metadata,
            name = "phrase_set",
            value = str(self.id))
        for sentence in matching_sentences:
            sentence.sentence.unit.properties.append(property)
            sentence.sentence.properties.append(property)
            sentence.sentence.save()
            sentence.sentence.unit.save()
        property.save()



class SentenceSet(Set):
    """A ``Set`` that can have a list of ``Sentences`` in it.

    The ``type`` attribute of a ``SentenceSet`` is set to ``sentenceset``.

    Attributes:
        sentences (list): A list of ``Sentence``\s in this ``SentenceSet``.
    """

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    sentences = db.relationship("Sentence",
        secondary="sentences_in_sentencesets",
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "sentence",
    }

    def get_items(self):
        """Return the ``Sentence``\s associated with this ``SentenceSet``.

        Returns:
            list of Sentences
        """
        return self.sentences

    def add_items(self, sentence_ids):
        """ Adds the sentences with the given ids to this set and adds metadata
        properties saying that these sentences are in this set."""
        sentences = Sentence.query.filter(
            Sentence.id.in_(sentence_ids))
        self.sentences.extend(sentences)
        self.save()
        metadata = PropertyMetadata.query.filter_by(
            property_name = "sentence_set").first()
        property = Property(
            project = self.project,
            property_metadata = metadata,
            name = "sentence_set",
            value = str(self.id))
        for sentence in sentences:
            sentence.unit.properties.append(property)
            sentence.properties.append(property)
            sentence.save()
            sentence.unit.save()
        property.save()

class DocumentSet(Set):
    """A Set that can have a list of ``Document``\s in it.

    The ``type`` attribute of a ``DocumentSet`` is set to ``documentset``.

    Attributes:
        documents (list): A list of ``Document``\s in this ``DocumentSet``.
    """

    id = db.Column(db.Integer, db.ForeignKey("set.id"), primary_key=True)
    documents = db.relationship("Document",
        secondary="documents_in_documentsets",
        backref="sets")

    __mapper_args__ = {
        "polymorphic_identity": "document",
    }

    def get_items(self):
        """Return the ``Document``s associated with this ``DocumentSet``.

        Returns:
            list of Documents
        """
        return self.documents

    def add_items(self, document_ids):
        """ Adds the documents with the given ids to this set and adds metadata
        properties saying that these documents and the affected sentences are in
        in this set."""
        documents = Document.query.filter(
           Document.id.in_(document_ids))
        self.documents.extend(documents)
        self.save()
        metadata = PropertyMetadata.query.filter_by(
           property_name = "document_set").first()
        property = Property(
           project = self.project,
           property_metadata = metadata,
           name = "document_set",
           value = str(self.id))
        for document in documents:
            document.properties.append(property)
            document.save()
            sentences = Sentence.query.filter(
                Sentence.document_id == document.id)
            for sentence in sentences:
                sentence.properties.append(property)
                sentence.unit.properties.append(property)
                sentence.save()
                sentence.unit.save()
        property.save()
