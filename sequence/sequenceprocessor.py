from sequence import Sequence

class SequenceProcessor(object):
    def __init__(self, reader_writer, grammatical_info_exists):
        # TODO: handle reader_writer once it's finished
        self.grammatical_info_exists = grammatical_info_exists

        self.stop_words.extend(pronouns + prepositions + determiners + \
            conjunctions + modal_verbs + primary_verbs + adverbs + \
            punctuation + contractions)

    def join_lemmas(self, words, delimiter):
        """Join the lemmas of words with the delimiter.

        :param list words: A list of TaggedWord objects with lemmas.
        :param str delimiter: A delimiter to put between lemmas.
        :return str: The combined lemmas.
        """

        lemmas = ""
        for word in words:
            lemmas += word.lemma + delimiter

        return lemmas

    def join_words(self, words, delimiter):
        """Join  words with the delimiter.

        :param list words: A list of TaggedWord objects.
        :param str delimiter: A delimiter to put between words.
        :return str: The combined words.
        """

        words = ""
        for word in words:
            words += word.word + delimiter

        return words

    def remove_stops(self, words):
        """Remove every sort of stop from the sentences.

        :param list words: A list of TaggedWord objects.
        :return list: The list without stops.
        """
        
        without_stops = []
        for word in words:
            if self.stop_words not in word.lower():
                without_stops.append(word)

        return without_stops

    def process(self, sentence):
        #TODO: implement timing?
        previously_indexed = []
        sequences = [] # a list of Sequences
        #TODO: there must be a way to make this nicer
        for i in range(0, len(sentence.tagged)):
            previously_indexed[i] = []
            for j in range(i+1, len(sentence.tagged) + 1):
                if j - i < 5:
                    wordlist = sentence.tagged[i:j]
                    lemmatized_phrase = self.join_lemmas(wordlist, " ")
                    surface_phrase = self.join_words(wordlist, " ")
                    words_nostops = self.remove_stops(wordlist)
                    lemmatized_phrase_nostops =
                        self.join_lemmas(words_nostops, " ")
                    surface_phrase_nostops =
                        self.join_words(words_nostops, " ")

                    #TODO: these assignments could maybe be done better
                    has_stops = len(words_nostops) < len(wordlist)
                    lemmatized_has_stops = len(lemmatized_phrase_nostop)
                    all_stop_words = len(words_nostops) == 0
                    lemmatized_all_stop_words = len(lemmatized_phrase_nostops) == 0

                    if not surface_phrase in previously_indexed[i]:
                        sequences.append(Sequence(start_position=i,
                            sentence_id=sentence.id,
                            document_id=sentence.document_id,
                            sequence=surface_phrase,
                            is_lemmatized=False,
                            has_function_words=has_stops,
                            all_function_words=all_stop_words,
                            words=wordlist))
                        previously_indexed[i].append(surface_phrase)
                        if has_stops and not all_stop_words and words_nostops[0] == wordlist[0]:
                            if not surface_phrase_nostop in previously_indexed[i]:
                                sequences.append(Sequence(start_position=i,
                                sentence_id=sentence.id,
                                document_id=sentence.document_id,
                                sequence=surface_phrase_nostop,
                                is_lemmatized=False,
                                has_function_words=False,
                                all_function_words=False,
                                words=words_nostop))

                        sequences.append(Sequence(start_position=i,
                            sentence_id=sentence.id,
                            document_id=sentence.document_id,
                            sequence=lemmatized_phrase,
                            is_lemmatized=True,
                            has_function_words=lemmatized_has_stops,
                            all_function_words=lemmatized_all_stop_words,
                            words=wordlist))
                        previously_indexed[i].append(lemmatized_phrase)
                        if not lemmatized_phrase_wothout_stops in previously_indexed[i]:
                            if lemmatized_has_stops and not lemmatized_all_stop_words and words_without_stops[0] == words[0]:
                                sequences.append(Sequence(start_position=i,
                                    sentence_id=sentence.id,
                                    document_id=sentence.document_id,
                                    sequence=lemmatized_phrase_mostops,
                                    is_lemmatized=True,
                                    has_function_words=False,
                                    all_function_words=False,
                                    words=words_nostops))
        for sequence in sequences:
            self.reader_writer.index_sequence(sequence)

        return True

    def finish(self):
        pass