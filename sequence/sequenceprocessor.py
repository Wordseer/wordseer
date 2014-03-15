import sequence

class SequenceProcessor(object):
    def __init__(reader_writer, grammatical_info_exists):
        # TODO: handle reader_writer once it's finished
        self.grammatical_info_exists = grammatical_info_exists

        self.stop_words.extend(pronouns + prepositions + determiners + \
            conjunctions + modal_verbs + primary_verbs + adverbs + \
            punctuation + contractions)

    def join_lemmas(words, delimiter):
        """Join the lemmas of words with the delimiter.

        :param list words: A list of TaggedWord objects with lemmas.
        :param str delimiter: A delimiter to put between lemmas.
        :return str: The combined lemmas.
        """

        lemmas = ""
        for word in words:
            lemmas += word.lemma + delimiter

        return lemmas

    def join_words(words, delimiter):
        """Join  words with the delimiter.

        :param list words: A list of TaggedWord objects.
        :param str delimiter: A delimiter to put between words.
        :return str: The combined words.
        """

        words = ""
        for word in words:
            words += word.word + delimiter

        return words

    def remove_stops(words):
        """Remove every sort of stop from the sentences.

        :param list words: A list of TaggedWord objects.
        :return list: The list without stops.
        """
        
        without_stops = []
        for word in words:
            if self.stop_words not in word.lower():
                without_stops.append(word)

        return without_stops

    def process(sentence):
        #TODO: implement timing?
        previously_indexed = {}
        ok = True
        sequences = [] # a list of Sequences
        #TODO: there must be a way to make this nicer
        for i in range(0, len(sentence.tagged)):
            previously_indexed["i", ""]
            for j in range(i+1, len(sentence.tagged) + 1):
                if j - i < 5:
                    words = sentence.tagged[i:j]
                    lemmatized_phrase = self.join_lemmas(words, " ")
                    surface_phrase = self.join_words(words, " ")
                    words_nostops = self.remove_stops(words)
                    lemmatized_phrase_nostops =
                        self.join_lemmas(words_nostops, " ")
                    surface_phrase_nostops =
                        self.join_words(words_nostops, " ")

                    #TODO: these assignments could maybe be done better
                    has_stops = len(words_nostops) < len(words)
                    lemmatized_has_stops = len(lemmatized_phrase_nostop)
            