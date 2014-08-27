"""Models for projects.
"""
from sqlalchemy.ext.associationproxy import association_proxy

from app import db
from base import Base
from .log import Log
from .association_objects import ProjectsUsers

class Project(db.Model, Base):
    """A WordSeer project for a collection of documents.

    Attributes:
        name (str): A human-readable name for this project.
        path (str): The location of the directory of the files of this project.
        user (User): The owner of this project.
        documents (list of Documents): ``Document``\s present in this project.
    """
    STATUS_UNPROCESSED = 0
    STATUS_PREPROCESSING = 1
    STATUS_DONE = 2

    STATUS_NAMES = {
        STATUS_UNPROCESSED: "Not yet procesed.",
        STATUS_PREPROCESSING: "Preprocessing.",
        STATUS_DONE: "Preprocessed."
    }

    # Attributes
    name = db.Column(db.String)
    path = db.Column(db.String)
    status = db.Column(db.Integer, default=STATUS_UNPROCESSED)

    # Active project indicator
    active_project = None

    # Relationships
    document_files = db.relationship("DocumentFile",
        secondary="document_files_in_projects", backref="projects")
    structure_files = db.relationship("StructureFile", backref="project")
    logs = db.relationship("Log", backref="project")
    word_in_sentence = db.relationship("WordInSentence",
        backref="project", lazy="dynamic")
    sequence_in_sentence = db.relationship("SequenceInSentence",
        backref="project", lazy="dynamic")
    word_in_sequence = db.relationship("WordInSequence",
        backref="project", lazy="dynamic")
    dependency_in_sentence = db.relationship("DependencyInSentence",
        backref="project", lazy="dynamic")
    users = association_proxy("project_users", "user",
        creator=lambda user: ProjectsUsers(user=user))

    def get_documents(self):
        """A method to get all the ``Document``\s that are in this project.

        Returns:
            list of ``Document``\s.
        """

        documents = []

        for document_file in self.document_files:
            documents.extend(document_file.documents)

        return documents

    def get_words(self):
        """Get all the ``Word``\s in this project.
        """

        pass

    def frequent_sequences(self, position, length, limit, lemmatized = False):
        """Return the most frequently occurring sequences with the given
        parameters.

        Unfortunately, for the sake of performance, we had to use a literal SQL
        query instead of ORM calls. Here is the breakdown of the query:
        - The SELECT statement gets the id and text of the sequence, as well as
          the sentence count from the count model associated with the sequence.
        - The INNER JOINs in the FROM clause serve simply to join together all
          relevant tables. There is a join for both count and sequence_count
          because of single-table inheritence that would normally be hidden
        - The WHERE conditionals are straightforward - they take the parameters
          from this method and filter the results by them
        - The GROUP BY serves to return entries that correspond to a sequence
        - Finally, we order by the counts and limit the results
        """

        return db.session.execute(
            """SELECT sequence.id, sequence.sequence, count.sentence_count
            FROM sequence INNER JOIN sequence_in_sentence
                ON sequence.id = sequence_in_sentence.sequence_id
                INNER JOIN sequence_count
                ON sequence.id = sequence_count.sequence_id
                INNER JOIN count ON sequence_count.id = count.id
            WHERE sequence_in_sentence.position = {position} AND
                sequence.length = {length} AND
                sequence.lemmatized = {lemmatized} AND
                count.project_id = {project_id}
            GROUP BY sequence.id
            ORDER BY count.sentence_count DESC
            LIMIT {limit}
        """.format(
            position = position,
            length = length,
            lemmatized = int(lemmatized),
            project_id = self.id,
            limit = limit
        )).fetchall()

    def frequent_words(self, part_of_speech, position, limit):
        """Return the most frequently occurring words with the given parameters.

        This query is similar to the one above; see above for explanation.

        Because this query groups by the lemma, some words get lost because they
        have the same lemma as another word. This doesn't make sense but it seems
        to be what the application wants.
        """

        return db.session.execute(
            """SELECT word.id, word.word, count.sentence_count
            FROM word INNER JOIN word_in_sentence
                ON word.id = word_in_sentence.word_id
                INNER JOIN word_count
                ON word.id = word_count.word_id
                INNER JOIN count ON word_count.id = count.id
            WHERE word_in_sentence.position = {position} AND
                word.part_of_speech LIKE '{part_of_speech}%' AND
                count.project_id = {project_id}
            GROUP BY word.id
            ORDER BY count.sentence_count DESC
            LIMIT {limit}
        """.format(
            position = position,
            part_of_speech = part_of_speech,
            project_id = self.id,
            limit = limit
        )).fetchall()

    def get_errors(self):
        """Return all ``ErrorLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "error").all()

    def get_warnings(self):
        """Return all ``WarningLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "warning").all()

    def get_infos(self):
        """Return all ``InfoLogs`` attached to this project.
        """
        return Log.query.filter(Log.project == self).\
            filter(Log.type == "info").all()

