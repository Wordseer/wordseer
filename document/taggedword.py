class TaggedWord:
    """
    This class describes a single tagged word.
    """
    
    space_before = " "

    def __init__(self, *args, **kwargs):
        """Instantiate a TaggedWord object.

        Kwargs:
            id (int): The ID for the word.
            word (str): The stored word.
            tag (str): Part of speech for the word.
            lemma (str): The lemma for this word.
        """
        for item, val in kwargs.items():
            setattr(self, item, val)

    def __str__(self):
        return self.word + "/" + self.tag + " - " + lemma