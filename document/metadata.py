"""
Keep track of metadata for Units.
"""
from mixins.comparebydict import CompareByDict
from mixins.argstodict import ArgsToDict

#TODO: documentation

class Metadata(CompareByDict, ArgsToDict):
    """This class holds metadata regarding a certain Unit, Sentence,
    or Document. Each Metadata object describes a certain property.
    """
    def __init__(self, **kwargs):
        """
        Instantiate a Metadata instance.

        :key string property_name: The name of the property.
        :key string parent_property_name:
        :key string value: The value of this property.
        :key int property_ID:
        :key boolean value_displayed:
        :key boolean name_displayed:
        :key string display_name:
        :key dict specification:
        """

        self.property_name = ""
        self.value = ""

        super(Metadata, self).__init__(**kwargs)

    def __str__(self):
        return self.property_name + ": " + self.value
