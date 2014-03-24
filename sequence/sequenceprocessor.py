from sequence import Sequence
import string

class SequenceProcessor(object):
    def __init__(self, reader_writer, grammatical_info_exists):
        # TODO: handle reader_writer once it's finished
        self.reader_writer = reader_writer
        self.grammatical_info_exists = grammatical_info_exists

        self.stop_words = []

        prepositions = string.split(("about away across against along"
            " around at behind beside besides by despite down during for from"
            " in inside into near of off on onto over through to toward with"
            " within whence until without upon hither thither unto up"), " ")

        pronouns = string.split(("i its it you your thou thine thee we"
            " he they me us her them him my mine her hers his our thy thine"
            " ours their theirs myself itself mimself ourselves herself"
            " themselves anything something everything nothing anyone"
            " someone everyone ones such"), " ")

        determiners = string.split(("the a an some any this these each"
            " that no every all half both twice one two first second other"
            " another next last many few much little more less most least"
            " several no own"), " ")

        conjunctions = string.split(("and or but so when as while"
            " because although if though what who where whom when why whose"
            " which how than nor not"), " ")

        modal_verbs = string.split(("can can't don't won't shan't"
            " shouldn't ca canst might may would wouldst will willst should"
            " shall must could"), " ")

        primary_verbs = string.split(("is are am be been being went go"
            " do did doth has have hath was were had"), " ")

        adverbs = string.split(("again very here there today tomorrow"
            " now then always never sometimes usually often therefore"
            " however besides moreover though otherwise else instead"
            " anyway incidentally meanwhile"), " ")

        punctuation = string.split((". ! @ # $ % ^ & * ( ) _ - -- --- +"
            " = ` ~  { } [ ] | \\ : ; \" ' < > ? , . / "), " ")

        contractions = string.split((" 's 'nt 'm n't th 'll o s"
            " 't 'rt "), " ")

        self.stop_words.extend(pronouns + prepositions + determiners +
            conjunctions + modal_verbs + primary_verbs + adverbs +
            punctuation + contractions)


    #TODO: these methods are almost identical
    def join_lemmas(self, words, delimiter):
        """Join the lemmas of words with the delimiter.

        :param list words: A list of TaggedWord objects with lemmas.
        :param str delimiter: A delimiter to put between lemmas.
        :return str: The combined lemmas.
        """

        lemmas = []
        for word in words:
            lemmas.extend([word.lemma, delimiter])

        return "".join(lemmas[:-1])

    def join_words(self, words, delimiter):
        """Join  words with the delimiter.

        :param list words: A list of TaggedWord objects.
        :param str delimiter: A delimiter to put between words.
        :return str: The combined words.
        """

        result = []
        for word in words:
            result.extend([word.word, delimiter])

        return "".join(result[:-1])

    def remove_stops(self, words):
        """Remove every sort of stop from the sentences.

        :param list words: A list of TaggedWord objects.
        :return list: The list without stops.
        """
        
        without_stops = []
        for word in words:
            if word.word.lower() not in self.stop_words:
                without_stops.append(word)

        return without_stops

    def process(self, sentence):
        """Iterate and record every five word long sequence. The method records
        using the ReaderWriter a list of sequences present in the given
        sentence.
        :param Sentence sentence: The sentence to process,
        :return boolean: True.
        """
        #TODO: implement timing?
        sequences = [] # a list of Sequences
        #TODO: there must be a way to make this nicer
        for i in range(0, len(sentence.tagged)):
            self.previously_indexed = []
            for j in range(i+1, len(sentence.tagged) + 1):
                if j - i < 5:
                    # For every sequence of five or fewer words, create a
                    # Sequence.
                    sequences.extend(self.get_sequence(sentence, i, j))

        #for sequence in sequences:
        #    self.reader_writer.index_sequence(sequence)

        return True

    def get_sequence(self, sentence, i, j):
        """Handle the main processing part in the process() loop.
        :param Sentence sentence: A sentence object to create sequences from.
        :param int i: The index to start the sequence from, inclusive.
        :param int j: The index to stop the sequence from, exclusive.
        :return list: A list of Sequences.
        """
        sequences = []
        
        wordlist = sentence.tagged[i:j]
        lemmatized_phrase = self.join_lemmas(wordlist, " ")
        surface_phrase = self.join_words(wordlist, " ")

        if surface_phrase in self.previously_indexed:
            #If we've already seen this sentence, don't bother
            return sequences
        
        wordlist_nostops = self.remove_stops(wordlist)
        lemmatized_phrase_nostops = self.join_lemmas(wordlist_nostops,
            " ")
        surface_phrase_nostops = self.join_words(wordlist_nostops, " ")

        #TODO: these assignments could maybe be done better
        has_stops = len(wordlist_nostops) < len(wordlist)
        lemmatized_has_stops = len(lemmatized_phrase_nostop)
        
        all_stop_words = len(wordlist_nostops) == 0
        lemmatized_all_stop_words = len(lemmatized_phrase_nostops) == 0

        sequences.append(Sequence(start_position=i,
            sentence_id=sentence.id,
            document_id=sentence.document_id,
            sequence=surface_phrase,
            is_lemmatized=False,
            has_function_words=has_stops,
            all_function_words=all_stop_words,
            words=wordlist))
        self.previously_indexed.append(surface_phrase)
        
        if (has_stops and not
            all_stop_words and
            wordlist_nostops[0] == wordlist[0] and not
            surface_phrase_nostop in self.previously_indexed):
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
            
        self.previously_indexed.append(lemmatized_phrase)
        
        if (not lemmatized_phrase_nostops in self.previously_indexed and
            lemmatized_has_stops and not
            lemmatized_all_stop_words and
            words_without_stops[0] == words[0]):
                sequences.append(Sequence(start_position=i,
                    sentence_id=sentence.id,
                    document_id=sentence.document_id,
                    sequence=lemmatized_phrase_mostops,
                    is_lemmatized=True,
                    has_function_words=False,
                    all_function_words=False,
                    words=wordlist_nostops))

        return sequences

    def finish(self):
        pass

