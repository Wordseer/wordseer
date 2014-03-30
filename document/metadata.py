from mixins.comparebydict import CompareByDict
from mixins.argstodict import ArgsToDict

#TODO: documentation

class Metadata(CompareByDict, ArgsToDict):
    def __init__(self, *args, **kwargs):
        """
        Instantiate a Metadata instance.

        Keword arguments:
        property_name
        parent_property_name
        value
        property_ID
        value_displayed
        name_displayed
        display_Name
        specification
        """

        self.property_name = ""
        self.value = ""

        super(Metadata, self).__init__(**kwargs)

    def __str__(self):
        return self.property_name + ": " + self.value
