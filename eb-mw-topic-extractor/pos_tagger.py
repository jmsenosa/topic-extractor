#!/usr/bin/python
# -*- coding: utf-8 -*-
import site_packages.nltk as nltk
from nltk.tag.perceptron import PerceptronTagger

import json
import data

import postItems

import codecs
import sentence_construction
# import tagalog_entities_extractor as tlentitiesExtractor
import tagalog_entities_extractor
tlentitiesExtractor = tagalog_entities_extractor.TagalogEntitiesExtractor()

import named_entity_recognizer
nameentityrecognizer = named_entity_recognizer.NameEntityRecognizer()

from custom_dictionary import englishwords


import text_preprocessing as tp

from pprint import pprint 
from nltk.corpus import wordnet as wn
from nltk import word_tokenize,sent_tokenize, pos_tag
from collections import Counter
import time
import sys
import re

# import site_packages.enchant as enchant
from site_packages.langdetect import detect

# import polyglot
# from polyglot.text import Text, Word
# from polyglot.detect import Detector

from package.tagsenttagalognltk import pos_tagging
tl_posTagger = pos_tagging.POS_tagger()

reload(sys)
sys.setdefaultencoding('utf8')

class PosTaggerClass(object):

    paraList       = []
    tagalogApos    = postItems.tagalogApos
    posEnglishFix  = postItems.posEnglishFix
    posDictionary  = postItems.posDictionary
    pos_dictionary = postItems.pos_dictionary
    english_vocab  = []
    # englishDist = englishwords.englishwords
    wordnet_funct = None


    tagalogPOSTagdict = tl_posTagger.tlenglish_postTag()

    def __init__(self, wnfunc):

        self.wordnet_funct = wnfunc 
        evocab = set(w.lower() for w in nltk.corpus.words.words())
        self.english_vocab = evocab

    def index(self, paragraph):

        if isinstance(paragraph, str):
            sentenceArr = self.getSentences(paragraph)
        else:
            sentenceArr = paragraph

        posArray = []

        for sentence in sentenceArr:
            item = self.wordTagging(sentence)
            posArray.append(item)

        return posArray

    # must create a list of words from a sentence and get pos tags.
    def wordTagging(self, sentence):
        posWords = []
        # text = nltk.word_tokenize(sentence)
        tagset = None
        start_time = time.time()
        try:
            tokens = nltk.word_tokenize(sentence)
        except UnicodeDecodeError:
            tokens = nltk.word_tokenize(sentence.decode('utf-8'))

        tagger = PerceptronTagger()
        pos_arrs = nltk.tag._pos_tag(tokens, tagset, tagger)
        for pos_arr in pos_arrs:
            pos = []
            pos.append(pos_arr[0])
            pos.append(pos_arr[1])
            # print pos_arr
            if pos_arr[1] in self.posDictionary:
                ppt = self.posDictionary[pos_arr[1]]
            else:
                ppt = "symbol"

            pos.append(ppt)
            posWords.append(pos)

        return posWords

    # accept list of sentences and turn them into multi-array
    def getSentences(self, sentenceList):
        paraItem = []
        sents = sent_tokenize(sentenceList)

        for sen in sents:
            paraItem.append(sen)
        return paraItem

    # fix unicode in a text
    def unicodetoUTF(self, wordsArray):
        countr = 0
        newWordsArray = []
        for word in wordsArray:
            word = tp.fix(word)
            a = word[0]
            utfWord = a.decode('utf8')

            nwInit = []
            nwInit.append(utfWord)
            nwInit.append(word[1])
            nwInit.append(word[2])
            # print nwInit
            nwInit.append(nwInit)

            countr = countr + 1
        return newWordsArray 

    def detectLanguange(self, words):
        return detect(words)

    def generateNamedEntities(self,text):

        nameEndtities = []
        tagged_sentences = []

        singleQoutationSymbol  = ["'","‘","’","'"]
        doubleQoutationSymbols = ['"',"``","“","”", "''"]

        for singleQoute in singleQoutationSymbol:
            text = text.replace(singleQoute, "'")
        for doubleQoute in doubleQoutationSymbols:
            text = text.replace(doubleQoute, '"')

        text = text.decode('string_escape')

        language = self.detectLanguange(text.decode('utf-8'))

        text = tp.fix(text)
        text = tp.trashremove(text)
        text = tp.contraction(text)

        if language == "tl" or language == "ms" or language == "ceb":
            text = "Randomlang " + text
            nameEndtities, tagged_sentences = self.extractFilipinoEntities(text)
        if language == "en":

            sentenceConstruction = sentence_construction.SentencePatter(self.wordnet_funct)
            # posArray = self.getSentences(text)
            words = self.wordTagging(text)
            tagged_sentences.append(words)

            words = sentenceConstruction.detectConstruction(words)
            pwords = sentenceConstruction.extractCapitalNamedEntities(words)


            if len(pwords) > 0:
                for possibleTopicAtom in pwords:
                    entity = " ".join(possibleTopicAtom)
                    nameEndtities.insert(len(nameEndtities),entity)

        nameentityrecognizer.pos_extractor(text)
        nameEndtities = nameentityrecognizer.checkhumanEntities(nameEndtities)

        return (tagged_sentences, nameEndtities)

    def extractFilipinoEntities(self, text):

        sentenceConstruction = sentence_construction.SentencePatter()
        text   = self.separateAyAt(text)
        words  = tl_posTagger.extract(text)

        counter = 0
        newword = []
        for xx in words:
            if xx[1] == "UNK":
                if xx[0][0] == "'" and len(xx[0]) > 1:
                    wordL = ["'",'UNK']
                    newword.append(wordL)
                    wordl = [xx[0].replace("'", ""),"N"]
                    # print wordl,"ma L"
                    newword.append(wordl)
                else:
                    newword.append(xx)
            else:
                newword.append(xx)
            counter = counter + 1

        words = newword

        words  = self.fixEnglishTags(words)
        enlishTagEnities = words

        entities = tlentitiesExtractor.extractEntities(text,words)

        return entities, words

    def fixEnglishTags(self, poswordArray):
        counter = 0
        forEngPos = []

        idx_to_remove = []

        for x in poswordArray:
            if x[0] and x[0] != "randomlang":
                forEngPos.append(x[0])
            else:
                idx_to_remove.append(x)

        for idx in idx_to_remove:
            poswordArray.remove(idx)

        forEngPos = nltk.pos_tag(forEngPos);

        for posword in poswordArray:
            if posword[0] and posword[0]!= "randomlang":
                if posword[1] == "UNK" or posword[1] == "":
                    # check if variable is not alphanumeric and is a symbol
                    if posword[0].isalnum():
                        if posword[0].isdigit():
                            poswordArray[counter][1] = "CD"
                        else:
                            if englishwords.check(posword[0]):
                                poswordArray[counter][1] = forEngPos[counter][1]
                                poswordArray[counter].append("EN")
                            else:
                                poswordArray[counter][1] = "FW"
                    else:

                        isFloat = False

                        try:
                           val = float(poswordArray[counter][0].replace(',',''))
                           isFloat = True
                        except ValueError:
                           isFloat = False

                        if isFloat:
                            poswordArray[counter][1] = "CD"
                        else:
                            poswordArray[counter][1] = "SYMBOL"

                else:
                    try:
                        poswordArray[counter][1] = self.posEnglishFix[posword[1]]
                    except KeyError:
                        pass
                    if englishwords.check(posword[0]):
                        poswordArray[counter].append("EN")
            counter = counter + 1

        return poswordArray

    def separateAyAt(self, text):
        wordpostList = text.split(" ")
        initWordList = []

        counter = 0
        for word in wordpostList:
            m = re.match(r"([A-Za-z]+[\'|\\'']+[\w]{0,1})", word)

            if m is not None:
                separated = word.split("'")

                if separated[1] == "y":
                    initWordList.insert(len(initWordList),separated[0])
                    initWordList.insert(len(initWordList),"ay")

                elif separated[1] == "t":
                    initWordList.insert(len(initWordList),separated[0])
                    initWordList.insert(len(initWordList),"at")

                else:
                    initWordList.insert(len(initWordList),word)
            else:
                initWordList.insert(len(initWordList),word)
        return " ".join(initWordList)

    def callnamedEntites(self,text):
         item1, item2 = self.generateNamedEntities(text)
         return item1, item2
