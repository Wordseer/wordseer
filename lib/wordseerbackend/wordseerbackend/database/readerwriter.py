from app.models import *
import pdb
from sqlalchemy.orm.exc import NoResultFound

from app import db

class ReaderWriter:

    Base.commit_on_save = False
    engine = db.engine

    @profile
    def write_parse_products(self, products):
        """Converts ParseProducts into the corresponding models and writes them
        into the database.

        The ParseProducts contain data for dependencies, grammatical
        relationships, and the sentences in which these are contained. The
        method iterates through the products, extracts the data, initializes
        the models, establishes the relationships between the models, and
        saves them into the database.
        """

        # print("product", str(products.__dict__))

        sentence_index = 0

        # Read in the parsed sentences
        for parse in products.parses:

            sentence = products.sentences[sentence_index]
            # NOTE: this assumes that the sentence indices match the parses

            # Read in the data for each dependency in the sentence
            for dep in parse.dependencies:

                connection = self.engine.connect()
                connection.execution_options(autocommit=False)
                with connection.begin() as trans:
                    # print(dep.__dict__)

                    # Retrieve the corresponding grammatical relationship, or
                    # create a new grammatical relationship.
                    relationship_id = None

                    try:
                        relationship_id = GrammaticalRelationship.query.filter_by(
                            name = dep.relationship
                        ).one().id
                    except(NoResultFound):
                        relationship_id = connection.execute(
                              GrammaticalRelationship.__table__.insert(),
                              { "name": dep.relationship }
                        ).inserted_primary_key[0]


                    # Read the data for the governor, and find the corresponding word
                    governor_data = parse.pos_tags[dep.gov_index]
                    governor_id = Word.query.filter_by(
                        word = governor_data.word[0],
                        lemma = governor_data.lemma,
                        tag = governor_data.tag
                    ).first().id

                    # Same as above for the dependent in the relationship
                    dependent_data = parse.pos_tags[dep.dep_index]
                    dependent_id = Word.query.filter_by(
                        word = dependent_data.word[0],
                        lemma = dependent_data.lemma,
                        tag = dependent_data.tag
                    ).first().id

                    # Create the dependency between the two words
                    dependency_id = None

                    try:
                        dependency_id = Dependency.query.filter_by(
                            grammatical_relationship_id = relationship_id,
                            governor_id = governor_id,
                            dependent_id = dependent_id
                        ).one().id
                    except(NoResultFound):
                        dependency_id = connection.execute(
                            Dependency.__table__.insert(),
                            {
                                "grammatical_relationship_id": relationship_id,
                                "governor_id": governor_id,
                                "dependent_id": dependent_id
                            }
                          ).inserted_primary_key[0]

                    # Add the dependency to the sentence
                    connection.execute(DependencyInSentence.__table__.insert(), {
                        "dependency_id": dependency_id,
                        "governor_index": dep.gov_index,
                        "dependent_index": dep.dep_index
                    })

                    #  print("relationship", relationship)
                    #  print("governor", governor)
                    #  print("dependent", dependent)
                    #  print("dependency", dependency)


            sentence_index += 1

        return products.sentences
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

    def create_new_document(self, doc, num_files):
        """Initialize the document and its subunits and save it to the database.

        This method calls a helper method to recursively initialize the subunit
        tree.
        """

        with self.engine.begin() as connection:

            document_unit_id = connection.execute(Unit.__table__.insert(), {
                "number": num_files,
                "type": "document",
            }).inserted_primary_key[0]

            document_id = connection.execute(Document.__table__.insert(), {
                "id": document_unit_id,
                "title": self._get_title(doc),
            }).inserted_primary_key[0]

            # TODO: add title as property

        subunit_number = 0
        for unit in doc.units:
            self._init_unit(unit, document_id, document_id, subunit_number)
            subunit_number += 1

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
        """Batch-process all sequences
        """

        connection = self.engine.connect()
        connection.execution_options(autocommit=False)

        with connection.begin() as trans:

            for sequence in sequences:
                sequence_id = connection.execute(Sequence.__table__.insert(), {
                    'sequence': sequence.sequence,
                    'lemmatized': sequence.is_lemmatized,
                    'has_function_words': sequence.has_function_words,
                    'all_function_words': sequence.all_function_words,
                    'length': len(sequence.words)
                }).inserted_primary_key[0]

                #print(new_sequence)
                #print("\n")

                connection.execute(SequenceInSentence.__table__.insert(), {
                  "sentence_id": sequence.sentence_id,
                  "sequence_id": sequence_id,
                  "position": sequence.start_position
                })

    def write_sequences(self):
        pass

    def finish_grammatical_processing(self):
        """Counts the number of documents and sentences in which each individual
        dependency and word appear.
        """

        return

        # Calculate counts for documents
        for document in Document.query.all():
            document.sentence_count = len(document.all_sentences)
            document.save()

        # Calculate counts for dependencies
        for dependency in Dependency.query.all():
            dependency.sentence_count = len(dependency.sentences)
            dependency.document_count = len(set([sentence.document for sentence in dependency.sentences]))
            dependency.save()


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

    def _init_unit(self, unit, document_id, parent_id, number):
        """Helper to recursively initialize subunits
        """

        with self.engine.begin() as connection:

            unit_id = connection.execute(Unit.__table__.insert(), {
                "number": number,
                "parent_id": parent_id
            }).inserted_primary_key[0]

            connection.execute(Property.__table__.insert(),
                [ { "name": property_data.property_name,
                    "value": property_data.value
                } for property_data in unit.metadata ]
            )


        for sentence_text in unit.sentences:

            connection = self.engine.connect()

            sentence_id = connection.execute(Sentence.__table__.insert(), {
                "text": sentence_text.text,
                "document_id": document_id,
                "unit_id": unit_id
            }).inserted_primary_key[0]

            position = 0
            for tagged_word in sentence_text.tagged:

                with connection.begin() as trans:

                    word_id = None
                    try:
                        word_id = Word.query.filter_by(
                            word = tagged_word.word[0],
                            lemma = tagged_word.lemma,
                            tag = tagged_word.tag
                        ).one().id
                    except NoResultFound:
                        word_id = connection.execute(Word.__table__.insert(), {
                            "word": tagged_word.word[0],
                            "lemma": tagged_word.lemma,
                            "tag": tagged_word.tag
                        }).inserted_primary_key[0]

                    connection.execute(WordInSentence.__table__.insert(), {
                        "word_id": word_id,
                        "sentence_id": sentence_id,
                        "position": position,
                        "space_before": tagged_word.space_before,
                        "tag": tagged_word.tag
                    })

                    position += 1

        subunit_number = 0
        for subunit in unit.units:
            self._init_unit(subunit, document_id, unit_id, subunit_number)
            subunit_number += 1

    def _get_title(self, doc):
        """Helper to find the title metadata from the list of metadata
        """

        title = ""

        for data in doc.metadata:
            if data.property_name.lower().strip() == "title":
                title = data.value

        return title

