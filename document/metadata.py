class Metadata:
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
        for key, value in kwargs.items():
            setattr(self, key, value)

        def __str__(self):
            return self.property_name + ": " + value