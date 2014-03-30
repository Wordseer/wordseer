#TODO: documentation
class Dependency(object):
    """This class describes the relationships between words through
    dependencies."""
    def __init__(self, relationship, governor, gov_index, dependent, dep_index,
        dep_pos, gov_pos):
        """
        :key str relationship: The name of the relationship described.
        :key str governor:
        :key int gov_index:
        :key str dependent:
        :key int dep_index:
        :key str dep_pos: This variable should not be modified.
        :key str gov_pos: This variable should not be modified.
        """

        self.relationship = relationship
        self.governor = governor
        self.gov_index = gov_index
        self.dependent = dependent
        self.dep_index = dep_index
        self._dep_pos = dep_pos
        self._gov_pos = gov_pos

    def __str__(self):
        return (self.relationship + "(" + self.governor + "-" + self.gov_index +
            ", " + self.dependent + "-" + self.dep_index + ")")
