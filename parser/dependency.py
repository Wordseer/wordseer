from mixins.kwargstodict import KwargsToDict

class Dependency(KwargsToDict):
    def __init__(self, *args, **kwargs):
        """
        :key str relationship:
        :key str governor:
        :key int gov_index:
        :key str dependent:
        :key int dep_index:
        :key str dep_pos: This variable should not be modified.
        :key str gov_pos: This variable should not be modified.
        """

        super(Dependency, self).__init__(**kwargs)

    def __str__(self):
        return (self.relationship + "(" + self.governor + "-" + self.gov_index +
            ", " + self.dependent + "-" + self.dep_index + ")")