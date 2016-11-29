import nltk
from nltk.corpus import stopwords

class NamedEntityRecognizer:
    def get_named_entities(self, text):
        sentences = nltk.sent_tokenize(text)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
        entity_names = []
        for tree in chunked_sentences:
            entity_names.extend(NamedEntityRecognizer.extract_entity_names(tree))
        return entity_names

    @staticmethod
    def extract_entity_names(tree):
        entity_names = []
        if tree.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in tree]))
        else:
            for child in tree:
                if isinstance(child, nltk.Tree):
                    entity_names.extend(NamedEntityRecognizer.extract_entity_names(child))
        return entity_names

    def recognize_all_entities(self, text):
        sentences = nltk.sent_tokenize(text)
        tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
        tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
        chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
        entity_names = []
        for tree in chunked_sentences:
            entity_names.extend(NamedEntityRecognizer.extract_entity_names(tree))
        return entity_names

    @staticmethod
    def extract_noun_phrases(tree):
        noun_phrases = []
        if tree.label() == 'NP':
            noun_phrases.append(' '.join([child[0] for child in tree]))
        else:
            for child in tree:
                if isinstance(child, nltk.Tree):
                    noun_phrases.extend(NamedEntityRecognizer.extract_noun_phrases(child))
        return noun_phrases

class NounPhraseExtractor:
    def __init__(self):
        self.lemmatizer = nltk.WordNetLemmatizer()
        self.grammar = grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    NP:
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
        {<NBAR>}
"""
        self.chunker = nltk.RegexpParser(grammar)
        self.stopwords = stopwords.words('english')

    def get_noun_phrases(self, text):
        tokens = nltk.word_tokenize(text)
        pos_tokens = nltk.pos_tag(tokens)
        tree = self.chunker.parse(pos_tokens)
        return list(self.get_terms(tree))

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
        for leaf in self.leaves(tree):
            term = " ".join([self.normalize(w) for w, t in leaf if self.acceptable_word(w) or t == "IN"])
            yield term