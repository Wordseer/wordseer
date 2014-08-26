import itertools
import math
import nltk
import string
import time

import wordseer.setup
import wordseer.search
import wordseer.util

from collections import defaultdict
from wordseer.util import punctuation


# Create the word to lemma dictionary to save database calls
word_to_lemma_dic = {}
def createWordToLemmaDictionary():
    global word_to_lemma_dic
    c = wordseer.setup.getCursor()
    sql = "SELECT DISTINCT(word), lemma from word ORDER BY lemma ASC"
    c.execute(sql)
    tokens = c.fetchall()
    c.close()
    for w in tokens:
        word_to_lemma_dic[w["word"].lower()] = w["lemma"].lower()

# Class to keep track all bigrams with w as the central word and
# wi within +/- 5 words of w.
class Bigram:
    def __init__(self, w, wi):
        self.w = w
        self.wi = wi
        self.p = [0] * 10
        self.freq = 0.0
        self.sent_ids = [set() for i in range(10)]

    # Sort instances of Bigram by wi
    def __lt__(self, other):
        return self.wi < other.wi

    def __str__(self):
        ret = self.w + " " + self.wi + " " + str(self.p)
        return ret

    # Equation (1a)
    def getStrength(self, fbar, sigma):
        return (self.freq - fbar) / sigma

    # Equation (1b)
    def getSpread(self):
        u = 0.0
        for i in range(0, 10):
            ps = self.p[i] - (self.freq / 10)
            u += (ps * ps)
        return u / 10

    # k1: Threshhold above which distances are interesting. Smadja suggests 1
    # Returns a list of relative positions to w in the range (-5, 5) excluding 0
    def getDistances(self, k1):
        # Equation (C_3)
        min_peak = (self.freq / 10) + (k1 * math.sqrt(self.getSpread()))

        distances = []
        for i in range(0, 5):
            if self.p[i] > min_peak:
                distances.append(i - 5)
        for i in range(5, 10):
            if self.p[i] > min_peak:
                distances.append(i - 4)
        return distances

    # Get the frequency of the bigram at offset from w
    # offset: The offset of wi compared to w
    def getp(self, offset):
        if offset < 0 and offset >= -5:
            return self.p[offset + 5]
        elif offset > 0 and offset <= 5:
            return self.p[offset + 4]
        return -1

    # Insert an instance of a bigram into this Bigram rooted at w
    # offset: The offset of wi compared to w
    def addInstance(self, offset, sent_id):
        if offset == 0:
            return

        assert (offset >= -5 and offset <= 5)
        if offset < 0:
            offset += 5
        elif offset > 0:
            offset += 4

        self.p[offset] += 1
        self.sent_ids[offset].add(sent_id)

        self.freq += 1

# Class to keep track of Bigrams that survived Stage 1
class S1Bigram:
    def __init__(self, w, wi, strength, spread, distances, sent_ids):
        self.w = w
        self.wi = wi
        self.strength = strength
        self.spread = spread
        self.distances = distances
        self.sent_ids = sent_ids

    def __str__(self):
        ret = self.w + " " + self.wi + " " + str(self.distances) + " " + str(self.sent_ids)
        return ret

# Class to keep track of many bigrams
class BigramCollection:
    WILDCARD_CHAR = "*"

    def __init__(self):
        self.bigrams = {}
        self.wfreq = 0.0

    def __len__(self):
        return len(self.bigrams)

    def splitSentenceToLemmas(self, sentence):
        global word_to_lemma_dic

        lemmas = []
        words = sentence.strip(string.punctuation).strip().split()
        for word in words:
            if word.lower() in word_to_lemma_dic:
                lemmas.append(word_to_lemma_dic[word.lower()])
        return lemmas

    def addSentence(self, query, sentence):
        global word_to_lemma_dic

        sent_id = sentence["id"]

        # Given the sentence ID, look up all the words & lemmas in this sentence
        # ordered by their position in the sentence.
        c = wordseer.setup.getCursor()
        sql = """SELECT lemma from sentence_xref_word
            where sentence_id = %s
            ORDER BY position ASC
            """
        c.execute(sql, (sent_id,))
        tokens = c.fetchall()
        c.close()

        # List of lemmas in the sentence
        lemmas = [w["lemma"].lower() for w in tokens]
        # lemmas = self.splitSentenceToLemmas(sentence["sentence"])

        # Find where query is located
        if query in word_to_lemma_dic:
            wLemmas = [word_to_lemma_dic[query]]
        else:
            wLemmas = [query]

        wIndex = -1
        for li, l in enumerate(lemmas):
            for wl in wLemmas:
                if l == wl:
                    wIndex = li
                    break
            if wIndex != -1:
                break

        # Take +/- 5 bigrams
        startIndex = max(wIndex - 5, 0)
        endIndex = min(wIndex + 5, len(lemmas) - 1)
        for i in range(startIndex, endIndex + 1):
            if lemmas[i] != query and lemmas[i] not in wordseer.util.punctuation:
                if not self.containsBigram(lemmas[i]):
                    self.bigrams[lemmas[i]] = Bigram(query, lemmas[i])

                # Update total count and specific bigram's count
                self.wfreq += 1
                self.bigrams[lemmas[i]].addInstance(i - wIndex, sent_id)

    def getFbar(self):
        return self.wfreq / len(self.bigrams)

    def getSigma(self):
        fbar = self.getFbar()
        term1 = 1.0 / float(len(self.bigrams) - 1)
        term2 = 0.0
        for key, bigram in self.bigrams.iteritems():
            x = bigram.freq - fbar
            term2 += (x * x)
        return math.sqrt(term1 * term2)

    # k0: Strength threshold (Smadja:  1)
    # k1: Distance threshold (Smadja:  1)
    # U0: Spread threshold   (Smadja: 10)
    def getStageOneBigrams(self, k0, k1, U0):
        passedStage = []
        for key, bigram in self.bigrams.iteritems():
            fbar = self.getFbar()
            sigma = self.getSigma()
            if bigram.getStrength(fbar, sigma) >= k0 and bigram.getSpread() >= U0:
                passedStage.append(S1Bigram(bigram.w, bigram.wi, bigram.getStrength(fbar, sigma), bigram.getSpread(), bigram.getDistances(k1), bigram.sent_ids))
        return passedStage

    # Go through all bigrams and calculate the total occurances of each position
    def getStageTwoBigrams(self, T):
        freqs = [0] * 10
        ngram = []

        for key, bigram in self.bigrams.iteritems():
            for i in range(0, 10):
                if i < 5:
                    pos = i - 5
                elif i >= 5:
                    pos = i - 4
                freqs[i] += bigram.getp(pos)

        for i in range(0, 10):
            query_added = False
            wordToAdd = self.WILDCARD_CHAR
            for key, bigram in self.bigrams.iteritems():

                if i < 5:
                    pos = i - 5
                elif i >= 5:
                    pos = i - 4

                # Add the actual word
                if i == 5 and not query_added:
                    ngram.append(bigram.w)
                    query_added = True

                if freqs[i] > 0 and (float(bigram.getp(pos)) / freqs[i]) > T:
                    wordToAdd = bigram.wi

            ngram.append(wordToAdd)

        # Remove "-" from the left and right
        start_i = -1
        for i, x in enumerate(ngram):
            if x != self.WILDCARD_CHAR:
                start_i = i
                break
        for i in range(len(ngram) - 1, -1, -1):
            if ngram[i] != self.WILDCARD_CHAR:
                end_i = i
                break

        return ngram[start_i:end_i + 1]

    def containsBigram(self, wi_):
        return wi_ in self.bigrams

# Calculates and returns the top phrases for query based on the Xtract algorithm by Smadja
def calculateTopPhrases(query):
    start_time = time.time()

    # Create word_to_lemma_dic before anything else
    createWordToLemmaDictionary()

    phrase_index = {}

    # FIXME: Only taking the first word for now
    query = query.split()[0].lower()

    # Get the sentences that match the query, matching all word forms
    foundSentences = wordseer.search.getMatchingSentencesByLemma(query)
    savedSentences = [x for x in foundSentences]

    # print "<p>At getMatchingSentencesByLemma: <b>%.3f seconds</b></p>" % (time.time() - start_time)

    # Add ALL sentences
    bigrams = BigramCollection()
    for sentence in savedSentences:
        bigrams.addSentence(query, sentence)

    # print "<p>Added bigrams: <b>%.3f seconds</b></p>" % (time.time() - start_time)

    # Retrieve Stage 1 output
    postStage1 = bigrams.getStageOneBigrams(1, 1, 10)

    # print "<p>Finished Stage 1: <b>%.3f seconds</b></p>" % (time.time() - start_time)

    # Proceed toward Stage 2
    for tempBG in postStage1:
        for d in tempBG.distances:
            offset = d
            if d < 0:
                offset += 5
            elif d > 0:
                offset += 4

            s2bigrams = BigramCollection()
            for stage2sent in [s for s in savedSentences if s["id"] in tempBG.sent_ids[offset]]:
                s2bigrams.addSentence(query, stage2sent)

            s2output = s2bigrams.getStageTwoBigrams(0.5)
            has_stop_words = hasStopWords(s2output)
            phrase = " ".join(s2output)
            if not allStopWords(s2output, query):
                if (not phrase_index.has_key(phrase)):
                    phrase_index[phrase] = newPhraseInfo(phrase, has_stop_words, True)
                phrase_index[phrase]["count"] += len(tempBG.sent_ids[offset])

    # print "<p>Finished Stage 2: <b>%.3f seconds</b></p>" % (time.time() - start_time)

    phrases = groupByPOSTags(phrase_index, query)
    phrase_id_index = {}
    ranked_phrase_ids = assignIDs(phrases, "lemma_", phrase_id_index, phrase_index)

    # print "<p>Done!: <b>%.3f seconds</b></p>" % (time.time() - start_time)

    return ranked_phrase_ids, phrase_id_index

def newPhraseInfo(phrase, has_stop_words, is_lemmatized):
    return {"count":0,
        "ids":set(),
        "phrase":phrase,
        "has_stop_words":has_stop_words,
        "is_lemmatized":is_lemmatized}

def allStopWords(words, query):
    """ Returns true if all the words in the given list are stop words, OR
        the only non-stop word is the query word.
    """
    for word in words:
        if not word.lower() in wordseer.util.STOP_WORDS and word.lower() != query:
            return False
    return True

def hasStopWords(words):
    """ Returns true if this list of words contains a stop word."""
    for word in words:
        if word.lower() in wordseer.util.STOP_WORDS:
            return True
    return False

def assignIDs(phrases, prefix, phrase_id_index, phrase_index):
    ranked_phrase_ids = []
    for i, phrase in enumerate(phrases):
        id = prefix + str(i)
        ranked_phrase_ids.append(id)
        phrase_index[phrase]["phrase_id"] = id
        phrase_id_index[id] = phrase_index[phrase]
    return ranked_phrase_ids

def groupByPOSTags(phrase_index, query):
    p2pos = {}
    counts = defaultdict(int)
    for p in phrase_index.keys():
        qloc = p.split().index(query)
        POS = [x[1] for x in nltk.pos_tag(nltk.word_tokenize(p))]
        POS[qloc] = query
        x = " ".join(POS)
        p2pos[p] = x
        counts[x] += phrase_index[p]["count"]

    # Sort, first by POS count, then by actual count
    def mycomp(x, y):
        if counts[p2pos[x]] < counts[p2pos[y]]:
            return -1
        elif counts[p2pos[x]] > counts[p2pos[y]]:
            return 1
        else:
            if phrase_index[x]["count"] < phrase_index[y]["count"]:
                return -1
            elif phrase_index[x]["count"] > phrase_index[y]["count"]:
                return 1
            else:
                return 0

    phrases = sorted(phrase_index.keys(), cmp=mycomp, reverse=True)
    return phrases

