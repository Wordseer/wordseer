#TODO: documentation
class Dependency(object):
    """This class describes the relationships between words through
    dependencies."""
    def __init__(self, relationship, governor, gov_index, gov_pos, dependent,
        dep_index, dep_pos):
        """
        :key str relationship: The name of the relationship between dependent
        and governor.
        :key str governor: The word that governs the dependent.
        :key int gov_index: The index of the governing word in the sentence.
        :key str dep_pos: Part of speech of the dependent. This variable should
            not be modified.
        :key str dependent: The word that's goverened by the governor.
        :key int dep_index: The index of dependent in the sentence.
        :key str gov_pos: Part of speech of the governor. This variable should
            not be modified.
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
