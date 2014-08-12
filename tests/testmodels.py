"""Tests for the ``app.wordseer.models`` module.
"""
import unittest

from app import db
from app.models import Dependency
from app.models import Document
from app.models import DocumentFile
from app.models import DocumentSet
from app.models import Property
from app.models import Project
from app.models import Sentence
from app.models import Set
from app.models import Sequence
from app.models import SequenceSet
from app.models import SentenceSet
from app.models import StructureFile
from app.models import Unit
from app.models import User
from app.models import Word
import database

class TestWordModel(unittest.TestCase):
    """Tests for the ``Word`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.clean()
        Project.active_project = Project()

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

        # NOTE: skipping because sentences should not be added like this
        # word_1.save()
        # word_2.save()

        # sen1 = Sentence()
        # sen2 = Sentence()

        # word_2.sentences = [sen1, sen2]

        # db.session.add_all([sen1, sen2])
        # db.session.commit()

        # assert word_2.sentences == [sen1, sen2]

class TestSentenceModel(unittest.TestCase):
    """Tests for the ``Sentence`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.clean()

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

        rel = sentence.add_word(word, position=4, space_before=" ",
            part_of_speech="ADF")

        assert rel.word == word
        assert rel.sentence == sentence
        assert rel.position == 4
        assert rel.space_before == " "
        assert rel.part_of_speech == "ADF"

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
        database.clean()

    def test_model_dependency(self):
        """Test to make sure that Dependency is working properly.
        """

        dependency = Dependency()
        dependency.save()

        # Test with sentences
        # NOTE: skipping because we should never add sentences like this
        # sentence1 = Sentence()
        # sentence2 = Sentence()
        # dependency.sentences = [sentence1, sentence2]

        # db.session.add_all([sentence1, sentence2])
        db.session.commit()

class TestSequenceModel(unittest.TestCase):
    """Tests for the ``Sequence`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.clean()

    def test_model_sequence(self):
        """Test to make sure that Sequence is working properly.
        """

        sequence = Sequence()
        sequence.save()

        # Test with Sentences
        # NOTE: skipping because we should never add sentences like this
        # sentence1 = Sentence()
        # sentence2 = Sentence()
        # sequence.sentences = [sentence1, sentence2]

        # db.session.add_all([sentence1, sentence2])
        db.session.commit()

class TestUnitModels(unittest.TestCase):
    """Tests for ``Unit`` and all models that inherit from ``Unit``.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.clean()

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
        assert unit.properties.all() == [unit_type, prop]

        unit.save()
        prop.save()

        retrieved_prop = Property.query.filter(Property.name=="title").\
            filter(Property.value == "Hello World").first()

        assert retrieved_prop.unit.type == "unit"
        assert retrieved_prop.unit.number == unit.number

    def test_model_document(self):
        """Test to make sure that Document is working properly.
        """

        d1 = Document(title="test")
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
        document_file = DocumentFile()
        document = Document()

        project.document_files = [document_file]
        document_file.documents = [document]
        user.projects = [project]

        user.save()
        project.save()
        document.save()
        document_file.save()

        assert document.belongs_to(user)

class TestPropertyModel(unittest.TestCase):
    """Tests for the ``Property`` model.
    """
    def setUp(self):
        """Clean the current database.
        """
        database.clean()

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
        database.clean()

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
        assert sets[0].get_items() == []

    def test_sentenceset(self):
        """Test the ``SentenceSet`` model.
        """

        sets = db.session.query(SentenceSet).all()

        assert len(sets) == 1
        assert self.sentenceset in sets
        assert sets[0].get_items() == []

    def test_documentset(self):
        """Test the ``DocumentSet`` model.
        """

        sets = db.session.query(DocumentSet).all()

        assert len(sets) == 1
        assert self.documentset in sets
        assert sets[0].get_items() == []

class TestStructureFileModel(unittest.TestCase):
    """Test the StructureFile model.
    """

    def setUp(self):
        database.clean()

    def test_model_structure_file(self):
        """Test to make sure that StructureFile is working properly.
        """

        structure_file1 = StructureFile(path="foo")
        structure_file2 = StructureFile(path="bar")

        project = Project()
        project.structure_files = [structure_file1, structure_file2]
        project.save()

        assert Project.query.all()[0].structure_files == [structure_file1,
            structure_file2]

class TestProjectModel(unittest.TestCase):
    """Tests for the Project model.
    """

    def setUp(self):
        database.clean()

    def test_get_documents(self):
        """Test the get_documents method.
        """
        document_file1 = DocumentFile()
        document_file2 = DocumentFile()

        document1 = Document()
        document2 = Document()
        document3 = Document()

        project = Project()

        document_file1.documents = [document1, document2]
        document_file2.documents = [document3]

        project.document_files = [document_file1, document_file2]
        project.save()

        assert project.get_documents() == [document1, document2, document3]


class TestDocumentFileModule(unittest.TestCase):
    """Test the DocumentFile model.
    """

    def setUp(self):
        database.clean()

    def test_model_document_file(self):
        """Test to make sure that DocumentFile is working properly.
        """

        documentfile = DocumentFile()
        document1 = Document()
        document2 = Document()
        project1 = Project()
        project2 = Project()

        documentfile.path = "/foo/bar"
        documentfile.documents = [document1, document2]
        documentfile.projects = [project1, project2]
        documentfile.save()

        assert len(documentfile.documents) == 2
        assert len(documentfile.projects) == 2

