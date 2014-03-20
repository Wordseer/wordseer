class Unit:
    """
    Units contain a list of sentences, or of other units. They also have
    metadata, an id, and a name.
    """

    def __init__(self, *args, **kwargs):
        """
        Construct a Unit.

        Keyword arguments:
        sentences -- a list of sentences.
        units -- a list of units.
        metadata -- an instance of Metadata
        id -- an integer id.
        name -- a name for the unit.
        """
        self.metadata = ""
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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__