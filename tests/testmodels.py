"""Tests for the ``app.wordseer.models`` module.
"""

import unittest

from app import db
from app.models import Dependency
from app.models import Document
from app.models import DocumentSet
from app.models import Property
from app.models import Sentence
from app.models import Set
from app.models import Sequence
from app.models import SequenceSet
from app.models import SentenceSet
from app.models import Unit
from app.models import Word
import database

class TestWordModel(unittest.TestCase):
    """Tests for the ``Word`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.restore_cache()

    def test_model_word(self):
        """Test to make sure that the atttributes of the Word model can be
        properly set.
        """

        string_1 = "hello"
        string_2 = "world"

        word_1 = Word()
        word_2 = Word()

        word_1.word = string_1
        word_2.word = string_2

        assert word_1.word == string_1
        assert word_2.word == string_2

        word_1.save()
        word_2.save()

        sen1 = Sentence()
        sen2 = Sentence()

        word_2.sentences = [sen1, sen2]

        db.session.add_all([sen1, sen2])
        db.session.commit()

        assert word_2.sentences == [sen1, sen2]

class TestSentenceModel(unittest.TestCase):
    """Tests for the ``Sentence`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.restore_cache()

    def test_model_sentence(self):
        """Test to make sure that Sentence is working properly.
        """

        text = "hello world"
        sentence = Sentence()
        sentence.text = text

        assert sentence.text == text

        word_1 = Word(word="hello")
        word_2 = Word(word="world")

        sentence.words.append(word_1)
        sentence.words.append(word_2)

        assert sentence.words == [word_1, word_2]

        sentence.save()

        #Test with Dependencies
        dependency1 = Dependency()
        dependency2 = Dependency()

        sentence.dependencies = [dependency1, dependency2]

        db.session.add_all([dependency1, dependency2])
        db.session.commit()

        #Test with Sequences
        sequence1 = Sequence()
        sequence2 = Sequence()

        sentence.sequences = [sequence1, sequence2]

        db.session.add_all([sequence1, sequence2])
        db.session.commit()

    def test_add_word(self):
        """Test the ``add_word()`` method of ``Sentence``.
        """

        sentence = Sentence(text="foo")
        word = Word(word="foo")

        sentence.save()
        word.save()

        rel = sentence.add_word(word, position=4, space_before=" ", tag="ADF")

        assert rel.word == word
        assert rel.sentence == sentence
        assert rel.position == 4
        assert rel.space_before == " "
        assert rel.tag = "ADF"

    def test_add_dependency(self):
        """Test the ``add_dependency()`` method of ``Sentence``.
        """

        sentence = Sentence(text="foo")
        dependency = Dependency(sentence_count=4)

        sentence.save()
        dependency.save()

        rel = sentence.add_dependency(dependency, governor_index=1,
            dependent_index=2)

        assert rel.dependency == dependency
        assert rel.sentence == sentence
        assert rel.governor_index == 1
        assert rel.dependent_index == 2

    def test_add_sequence(self):
        """Test the ``add_sequence()`` method of ``Sentence``.
        """

        sentence = Sentence(text="foo")
        sequence = Sequence(lemmatized=False)

        sentence.save()
        sequence.save()

        rel = sentence.add_sequence(sequence, position=1)

        assert rel.sequence == sequence
        assert rel.sentence == sentence
        assert rel.position == 1

class TestDependencyModel(unittest.TestCase):
    """Tests for the ``Depenedency`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.restore_cache()

    def test_model_dependency(self):
        """Test to make sure that Dependency is working properly.
        """

        dependency = Dependency()
        dependency.save()

        # Test with sentences
        sentence1 = Sentence()
        sentence2 = Sentence()
        dependency.sentences = [sentence1, sentence2]

        db.session.add_all([sentence1, sentence2])
        db.session.commit()

class TestSequenceModel(unittest.TestCase):
    """Tests for the ``Sequence`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.restore_cache()

    def test_model_sequence(self):
        """Test to make sure that Sequence is working properly.
        """

        sequence = Sequence()
        sequence.save()

        # Test with Sentences
        sentence1 = Sentence()
        sentence2 = Sentence()
        sequence.sentences = [sentence1, sentence2]

        db.session.add_all([sentence1, sentence2])

class TestUnitModels(unittest.TestCase):
    """Tests for ``Unit`` and all models that inherit from ``Unit``.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.restore_cache()

    def test_model_unit(self):
        """Test to make sure that Unit is working properly.
        """

        unit_type = Property(name="unit_type", value="section")
        number = 1

        unit = Unit()

        unit.properties = [unit_type]
        unit.number = number

        assert unit.number == number

        sentence = Sentence()
        sentence.words = [Word(word="hello"), Word(word="world")]
        prop = Property(name="title", value="Hello World")

        unit.sentences.append(sentence)
        unit.properties.append(prop)

        assert unit.sentences == [sentence]
        assert unit.properties == [unit_type, prop]

        unit.save()
        prop.save()

        retrieved_prop = Property.query.filter(Property.name=="title").\
            filter(Property.value == "Hello World").first()

        assert retrieved_prop.unit.type == "unit"
        assert retrieved_prop.unit.number == unit.number

    def test_model_document(self):
        """Test to make sure that Document is working properly.
        """

        d1 = Document(title="test", path="/path/to/d1")
        d1.save()

        assert d1.type == "document"

        u1 = Unit()
        u1.save()

        d1.children.append(u1)
        d1.save()

        assert d1.children == [u1]
        assert u1.parent == d1

    def test_document_belongs_to(self):
        """Check if ``belongs_to()`` on ``Document`` is working properly.
        """

        user = User()
        project = Project()
        document = Document()

        project.documents = [document]
        user.projects = [project]

        user.save()
        project.save()
        document.save()

        assert document.belongs_to(user)

class TestPropertyModel(unittest.TestCase):
    """Tests for the ``Property`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.restore_cache()

    def test_model_property(self):
        """Test to make sure that Property is working properly.
        """

        prop = Property()

        name = "title"
        value = "Hello World"

        prop.name = name
        prop.value = value

        assert prop.name == name
        assert prop.value == value

        prop.save()

        retrieved_prop = Property.query.filter(name=="title").\
            filter(value == "Hello World").first()

        assert retrieved_prop.name == prop.name
        assert retrieved_prop.value == prop.value

class TestSetsModels(unittest.TestCase):
    """Test all the different ``Set`` models.
    """

    @classmethod
    def setUpClass(cls):
        database.restore_cache()

        cls.set = Set()
        cls.sequenceset = SequenceSet()
        cls.sentenceset = SentenceSet()
        cls.documentset = DocumentSet()

        db.session.add_all([cls.set, cls.sequenceset, cls.sentenceset,
            cls.documentset])
        db.session.commit()

    def test_set(self):
        """Test to make sure that ``Set`` is working.
        """

        sets = db.session.query(Set).all()

        set2 = Set()
        self.set.children = [set2]
        set2.save()

        assert set2.parent == self.set
        assert self.set.children == [set2]

        assert len(sets) == 4
        assert self.set in sets

    def test_sequenceset(self):
        """Test the ``SequenceSet`` model.
        """

        sets = db.session.query(SequenceSet).all()

        assert len(sets) == 1
        assert self.sequenceset in sets

    def test_sentenceset(self):
        """Test the ``SentenceSet`` model.
        """

        sets = db.session.query(SentenceSet).all()

        assert len(sets) == 1
        assert self.sentenceset in sets

    def test_documentset(self):
        """Test the ``DocumentSet`` model.
        """

        sets = db.session.query(DocumentSet).all()

        assert len(sets) == 1
        assert self.documentset in sets

