"""
Metadata objects can describe a Unit, a Sentence, or a Document. They are
used to store certain information about the object in question.
"""
from mixins.comparebydict import CompareByDict
from mixins.kwargstodict import KwargsToDict

class Metadata(CompareByDict, KwargsToDict):
    """This class holds metadata regarding a certain Unit, Sentence,
    or Document. Each Metadata object describes a certain property.
    """
    def __init__(self, **kwargs):
        """
        Instantiate a Metadata instance.

        :key string property_name: The name of the property.
        :key string parent_property_name: ORPHAN
        :key string value: The value of this property.
        :key int property_ID: ORPHAN
        :key boolean value_displayed: ORPHAN
        :key boolean name_displayed: ORPHAN
        :key string display_name: ORPHAN
        :key dict specification: The JSON description of this type of metadata
        field.
        """

        self.property_name = ""
        self.value = ""

        super(Metadata, self).__init__(**kwargs)

    def __str__(self):
        return self.property_name + ": " + self.value
