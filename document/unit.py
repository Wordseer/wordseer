from comparebydict import CompareByDict

class Unit(CompareByDict):
    """
    Units contain a list of sentences, or of other units. They also have
    metadata, an id, and a name.
    """

    def __init__(self, *args, **kwargs):
        """Construct a Unit.

        Keyword arguments:
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
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        s = self.metadata.__str__()

        for u in self.units:
            s += u.__str__() + "\n"

        for s in self.sentences:
            s += s.__str__() + "\n"

        return s
