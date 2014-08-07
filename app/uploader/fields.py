"""
Custom fields for this flask application.
"""

from wtforms.fields import Field, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput, RadioInput

from .widgets import ButtonWidget

class ButtonField(Field):
    """A field to conveniently use buttons in flask forms.
    """
    widget = ButtonWidget()

    def __init__(self, text=None, name=None, value=None, **kwargs):
        """Standard init objects for a field, with the exception that the
        first argument will set the text of the button. Buttons don't have
        labels, so it doesn't make sense to have lable arguments.
        """
        super(ButtonField, self).__init__(**kwargs)
        self.text = text
        self.value = value
        if name is not None:
            self.name = name

    def _value(self):
        """Return the text of the button.
        """
        return str(self.text)

class MultiRadioField(SelectMultipleField):
    """A multiple-select, except displays a list of radio buttons.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed radio fields.
    """

    widget = ListWidget(prefix_label=False)
    option_widget = RadioInput()

    def add_choice(self, choice_id, choice_data):
        """Add a tuple to the choices property of the selection field. A bit
        shorter than typing out the full command.

        Arguments:
            choice_id (int): The first item in the tuple. From a template, this
                value is reachable as the .id attribute of every item in the
                selectionfield.
            choice_data: The second item in the tuple. From a template,
                this value is reachable as the .data attribute of every item in
                the selection field.
        """

        self.choices.append((choice_id, choice_data))

    def delete_choice(self, choice_id, choice_data):
        """The reverse of add_choice: remove a choice from the choices property
        of the selection field.

        Arguments:
            choice_id (int): The first item in the tuple. From a template, this
                value is reachable as the .id attribute of every item in the
                selection field.
            choice_data: The second item in the tuple. From a template, this
                value is reachable as the .data attribute of every item in the
                selection field.
        """

        self.choices.remove((choice_id, choice_data))

class MultiCheckboxField(SelectMultipleField):
    """A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

    def add_choice(self, choice_id, choice_data):
        """Add a tuple to the choices property of the selection field. A bit
        shorter than typing out the full command.

        Arguments:
            choice_id (int): The first item in the tuple. From a template, this
                value is reachable as the .id attribute of every item in the
                selectionfield.
            choice_data: The second item in the tuple. From a template,
                this value is reachable as the .data attribute of every item in
                the selection field.
        """

        self.choices.append((choice_id, choice_data))

    def delete_choice(self, choice_id, choice_data):
        """The reverse of add_choice: remove a choice from the choices property
        of the selection field.

        Arguments:
            choice_id (int): The first item in the tuple. From a template, this
                value is reachable as the .id attribute of every item in the
                selection field.
            choice_data: The second item in the tuple. From a template, this
                value is reachable as the .data attribute of every item in the
                selection field.
        """

        self.choices.remove((choice_id, choice_data))

