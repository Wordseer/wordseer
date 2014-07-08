from ..mixins.comparebydict import CompareByDict
from ..mixins.kwargstodict import KwargsToDict

class Unit(CompareByDict, KwargsToDict):
    """
    Units contain a list of sentences, or of other units. They also have
    metadata, an id, and a name.
    """

    def __init__(self, **kwargs):
        """Construct a Unit.

        :keyword list sentences: A list of Sentence objects in this unit.
        :keyword list units: A list of Unit objects in this unit.
        :keyword list metadata: A list of Metadata objects to describe this
        unit.
        :keyword int id: An id number for this unit.
        :keyword str name: A name for the unit.
        """

        self.metadata = []
        self.units = []
        self.sentences = []

        super(Unit, self).__init__(**kwargs)

    def __str__(self):
        output = str(self.metadata)

        for unit in self.units:
            output += str(unit) + "\n"

        for sentence in self.sentences:
            output += str(sentence) + "\n"

        return output
