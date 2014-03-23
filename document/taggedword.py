from comparebydict import CompareByDict

class TaggedWord(CompareByDict):
    """
    This class describes a single tagged word.
    """
    
    space_before = " "

    def __init__(self, *args, **kwargs):
        """Instantiate a TaggedWord object.

        :keyword int id: The ID for the word.
        :keyword str word: The stored word.
        :keyword str tag: Part of speech for the word.
        :keyword str lemma: The lemma for this word.
        """

        self.word = ""
        self.tag = ""
        self.lemma = ""

        for item, val in kwargs.items():
            setattr(self, item, val)

    def __str__(self):
        return self.word + "/" + self.tag + " - " + lemma
