"""This is the ORM implementation of the reader writer. It has performance issues
and is left here mostly for reference.
"""

from app.models import *
import pdb
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

from app import db
class ReaderWriter:

    Base.commit_on_save = False

    def write_parse_products(self, products):
        """Converts ParseProducts into the corresponding models and writes them
        into the database.

        The ParseProducts contain data for dependencies, grammatical
        relationships, and the sentences in which these are contained. The
        method iterates through the products, extracts the data, initializes
        the models, establishes the relationships between the models, and
        saves them into the database.
        """

        relationships = dict()
        dependencies = dict()

        sentence_ids = []
        # Read in the parsed sentences
        for parse in products:

            # Read in the data for each dependency in the sentence
            for dep in parse["dependencies"]:
                # print(dep.__dict__)

                # Retrieve the corresponding grammatical relationship, or
                # create a new grammatical relationship.
                key = dep["grammatical_relationship"]

                if key in relationships.keys():
                    relationship = relationships[key]
                else:

                    try:
                        relationship = GrammaticalRelationship.query.filter_by(
                            name = key
                        ).one()
                    except(MultipleResultsFound):
                        print("ERROR: duplicate records found for:")
                        print("\t" + str(key))
                    except(NoResultFound):
                        relationship = GrammaticalRelationship(
                            name = key
                        )
                        
                    relationships[key] = relationship

                # Read the data for the governor, and find the corresponding word
                governor = Word.query.filter_by(
                    word = dep["governor"],
                    lemma = dep["governor_lemma"],
                    tag = dep["governor_pos"]
                ).first()

                # Same as above for the dependent in the relationship
                dependent = Word.query.filter_by(
                    word = dep["dependent"],
                    lemma = dep["dependent_lemma"],
                    tag = dep["dependent_pos"]
                ).first()

                key = (relationship, governor, dependent)

                if key in dependencies.keys():
                    dependency = dependencies[key]
                else:

                    try:
                        dependency = Dependency.query.filter_by(
                            grammatical_relationship = relationship,
                            governor = governor,
                            dependent = dependent
                        ).one()
                    except(MultipleResultsFound):
                        print("ERROR: duplicate records found for:")
                        print("\t" + str(key))
                    except(NoResultFound):
                        dependency = Dependency(
                            grammatical_relationship = relationship,
                            governor = governor,
                            dependent = dependent
                        )
                        
                    dependencies[key] = dependency

                # Add the dependency to the sentence
                dependency_in_sentence = DependencyInSentence(
                    sentence_id = dep["sentence_id"],
                    dependency = dependency,
                    governor_index = dep["governor_index"],
                    dependent_index = dep["dependent_index"],
                )

                #  print("relationship", relationship)
                #  print("governor", governor)
                #  print("dependent", dependent)
                #  print("dependency", dependency)

                dependency_in_sentence.save()
                dependency.save()
                sentence_ids.append(dep["sentence_id"])

        db.session.commit()

        return [ Sentence.query.get(id) for id in sentence_ids ]
        # TODO: figure out what the output is really supposed to be

    def list_document_ids(self):
        """Get a list of document IDs.

        TODO: add collection support
        """

        return [ document.id for document in Document.query.all() ]

    def get_document(self, doc_id):
        """Return the document corresponding to the ID.
        """

        return Document.query.get(doc_id)

    
    def create_new_document(self, document, num_files):
        """Initialize the document and its subunits and save it to the database.

        This method calls a helper method to recursively initialize the subunit
        tree.
        """

        document.number = num_files

        [ _init_unit(child, document) for child in document.children ]            

        document.save()
        db.session.commit()
        return document

    def index_sequence(self, sequence):
        """Reads in sequence data to create and save sequeunces into the
        database.

        TODO: figure out if this is where sequences are supposed to be created,
        or if this is supposed to do something else
        """

        # Find the sentence that this sequence belongs to
        sentence = Sentence.query.get(sequence.sentence_id)

        new_sequence = Sequence(
            sequence = sequence.sequence,
            lemmatized = sequence.is_lemmatized,
            has_function_words = sequence.has_function_words,
            all_function_words = sequence.all_function_words,
            length = len(sequence.words)
        )

        #print(new_sequence)
        #print("\n")

        new_sequence.save()
        sentence.add_sequence(new_sequence, sequence.start_position)

    def index_sequences(self, sequences):
        """Batch-save sequences
        """

        # Find the sentence that this sequence belongs to
        for sequence in sequences:
            sentence = Sentence.query.get(sequence["sentence_id"])

            new_sequence = Sequence(
                sequence = sequence["sequence"],
                lemmatized = sequence["is_lemmatized"],
                has_function_words = sequence["has_function_words"],
                all_function_words = sequence["all_function_words"],
                length = len(sequence["words"])
            )

            #print(new_sequence)
            #print("\n")

            new_sequence.save()
            sentence.add_sequence(new_sequence, sequence["start_position"])


    def write_sequences(self):
        db.session.commit()

    def finish_grammatical_processing(self):
        """Counts the number of documents and sentences in which each individual
        dependency and word appear.
        """

        # Calculate counts for documents
        for document in Document.query.all():
            document.sentence_count = len(document.all_sentences)
            document.save()

        # Calculate counts for dependencies
        for dependency in Dependency.query.all():
            dependency.sentence_count = len(dependency.sentences)
            dependency.document_count = len(set([sentence.document for sentence in dependency.sentences]))
            dependency.save()

        db.session.commit()

    def finish_indexing_sequences(self):
        """For each sequence, count the number of sentences and documents
        in which it appears.
        """

        pass

    def calculate_word_counts(self):
        pass

    def calculate_tfidfs(self):
        pass

    def calculate_lin_similarities(self):
        pass

"""
Helpers
"""


def _init_unit(unit, document):
    """Helper to recursively initialize subunits
    """

    words = dict()

    for sentence_data in unit.sentence_data:
        sentence = Sentence(text=sentence_data["text"])
        sentence.document = document

        position = 0
        for word_data in sentence_data["words"]:

            key = (word_data["word"], word_data["lemma"], word_data["tag"])

            if key in words.keys():
                word = words[key]
                print("In dict " + str(word))
            else:

                try:
                    word = Word.query.filter_by(
                        word = word_data["word"],
                        lemma = word_data["lemma"],
                        tag = word_data["tag"]
                    ).one()
                    print("Found word " + str(word))
                except(MultipleResultsFound):
                    print("ERROR: duplicate records found for:")
                    print("\t" + str(key))
                except(NoResultFound):
                    word = Word(
                        word = key[0],
                        lemma = key[1],
                        tag = key[2]
                    )
                    print("New word " + str(word))
                    
                words[key] = word

            sentence.add_word(
                word = word,
                position = position,
                space_before = "", # word["space_before"],
                tag = word.tag
            )

    db.session.commit()

    subunit_number = 0
    for subunit in unit.children:
        new_subunit = _init_unit(subunit, document)
        new_subunit.number = subunit_number

    unit.save()
    return unit

def _get_title(doc):
    """Helper to find the title metadata from the list of metadata
    """

    title = ""

    for data in doc.metadata:
        if data.property_name.lower().strip() == "title":
            title = data.value

    return title

