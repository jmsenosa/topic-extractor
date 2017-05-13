import site_packages.nltk as nltk

import sys
import os

project_dir = os.path.dirname(__file__)
package_dir = project_dir+"/site_packages"
nltk_dir = project_dir+"/package/nltk_data"

from nltk.corpus import wordnet as wn
from nltk.util import ngrams # from nltk
from collections import Counter

class NLTK_helpers(object):
    
    wordnetFunc = None

    def __init__(self):
        self.wordnetFunc = wn 
        return

    def loadEvocab():
        evocab = set(w.lower() for w in nltk.corpus.words.words())
        return evocab

    # check default possible pos of a word
    def detectPOSofWord(self, word):
        synsets = wn.synsets( word )
        allPOSofWord = []

        for synset in synsets:
            initPOS = synset.lexname()
            pos = initPOS.split('.')

            allPOSofWord.append(str(pos[0]))
        allPOSofWord = Counter(allPOSofWord)

        return allPOSofWord

    # finding a term in a string (can be any # of words) , similar to present_in() but I/O: two params (string, string) - (raw text, keyword to be searched) / boolean
    def find_term(text, term):
        try:
            tokens = nltk.word_tokenize(text)
        except UnicodeDecodeError:
            tokens = nltk.word_tokenize(text.decode('utf-8'))
        except UnicodeEncodeError:
            tokens = nltk.word_tokenize(text.encode('utf-8'))
        term_token = term.split()
        value = False
        n_grams = list(ngrams(tokens, len(term_token)))
        for n in n_grams:
            if list(n) == term_token:
                value = True
                break
        return value




