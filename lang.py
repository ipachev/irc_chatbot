import nltk
from nltk.corpus import stopwords


class NounPhraseExtractor:
    def __init__(self):
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.grammar = grammar = r"""
    NOUN:
        {<VBG|NN.*|JJ|>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    ENTITY:
        {<VBG|NN|NE.*|JJ|>*<NE.*>}
        {<NE.*><VBG|NN|NE|JJ|>*<NN.*>}

    EP:
        {<NOUN|ENTITY><IN>?<ENTITY>}
        {<ENTITY><IN>?<NOUN|ENTITY>}
        {<ENTITY>}

    NP:
        {<NOUN><IN>?<NOUN>}  # Above, connected with in/of/etc...
        {<NOUN>}
"""
        self.chunker = nltk.RegexpParser(grammar)
        self.stopwords = stopwords.words('english')

    def get_noun_phrases(self, text):
        """
        Extract noun phrases from text, prioritizing the ones that contain named entities.
        :param text: The text to extract noun phrases from.
        :return: A list of noun phrases sorted by the ones that contain named entities first
        """
        tokens = nltk.word_tokenize(text)
        pos_tokens = nltk.pos_tag(tokens)
        ne_tokens = nltk.ne_chunk(pos_tokens, binary=True)
        tree = self.chunker.parse(ne_tokens)
        return self.get_terms(tree)

    def named_leaves(self, tree):
        """Finds NP (nounphrase) leaf nodes of a chunk tree."""
        for subtree in tree.subtrees(filter=lambda t: t.label() == 'EP'):
            yield subtree.leaves()

    def leaves(self, tree):
        """Finds NP (nounphrase) leaf nodes of a chunk tree."""
        for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
            yield subtree.leaves()


    def normalize(self, word):
        """Normalises words to lowercase and lemmatizes it."""
        word = word.lower()
        word = self.lemmatizer.lemmatize(word)
        return word


    def acceptable_word(self, word):
        """Checks conditions for acceptable word: length, stopword."""
        return 2 <= len(word) <= 40 and word.lower() not in self.stopwords


    def get_terms(self, tree):
        terms = []
        for leaf in self.named_leaves(tree):
            term = " ".join([self.normalize(w) for w, t in leaf if self.acceptable_word(w) or t == "IN"])
            terms.append(term)
        for leaf in self.leaves(tree):
            term = " ".join([self.normalize(w) for w, t in leaf if self.acceptable_word(w) or t == "IN"])
            terms.append(term)
        return terms


from unittest import TestCase

class TestStuff(TestCase):
    def setUp(self):
        self.npe = NounPhraseExtractor()

    def test(self):
        terms = self.npe.get_noun_phrases("I am from the capital of California and I like to write in programming languages")
        self.assertTrue("capital of california" == terms[0])
        self.assertTrue("programming language" == terms[1])

        terms = self.npe.get_noun_phrases("I like to write in programming languages and I am from the capital of California")
        self.assertTrue("capital of california" == terms[0])
        self.assertTrue("programming language" == terms[1])

        terms = self.npe.get_noun_phrases("I like to write in programming languages and I am from the city of Los Angeles")
        self.assertTrue("city of los angeles" == terms[0])
        self.assertTrue("programming language" == terms[1])

        terms = self.npe.get_noun_phrases("I like to write in programming languages and I am from Mexico city")
        self.assertTrue("mexico city" == terms[0])
        self.assertTrue("programming language" == terms[1])