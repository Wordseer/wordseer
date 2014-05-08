from mixins.comparebydict import CompareByDict
from mixins.kwargstodict import KwargsToDict

class TaggedWord(CompareByDict, KwargsToDict):
    """
    This class describes a single tagged word.
    """

    space_before = " "

    def __init__(self, **kwargs):
        """Instantiate a TaggedWord object.

        :keyword int id: The ID for the word.
        :keyword str word: The stored word.
        :keyword str tag: Part of speech for the word.
        :keyword str lemma: The lemma for this word.
        """

        self.word = ""
        self.tag = ""
        self.lemma = ""

        super(TaggedWord, self).__init__(**kwargs)

    def __str__(self):
        return self.word + "/" + self.tag + " - " + self.lemma
