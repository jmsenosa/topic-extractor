# -*- coding: utf-8 -*-

# from nltk.corpus import wordnet as wn
from collections import Counter
from itertools import groupby
import helper
import re
import sys
import postItems
reload(sys)
sys.setdefaultencoding('utf8')
# this code is called "The flying spaghetti monster"
# it has spaghetti and meat balls
class SentencePatter(object):

    starter               = postItems.starter
    stoppers              = postItems.stoppers
    posIndexer            = postItems.posIndexer
    notallowed            = postItems.notallowed
    name_suffixes         = postItems.name_suffixes
    qoutationSymbols      = postItems.qoutationSymbols
    spanish_connector     = postItems.spanish_connector
    sentencePOS_Array     = postItems.sentencePOS_Array
    sentenceWordsArray    = postItems.sentenceWordsArray
    conjuctionsintitles   = postItems.conjuctionsintitles
    spanish_connector_two = postItems.spanish_connector_two

    wordnet_funct = None


    def __init__(self,wnfunct):

        self.wordnet_funct = wnfunct
        self.sentenceWordsArray = self.sentencePOS_Array  = []
        return

    def detectConstruction(self, sentenceArray):
        # self.sentenceArray = sentenceArray;
        self.sentencePOS_Array = []
        self.sentenceWordsArray = []


        for wordPos in sentenceArray:
            if wordPos[1].isalnum() == False:
                wordPos[1] = 'SYMBOL'
            self.sentencePOS_Array.append(wordPos[1])
            self.sentenceWordsArray.append(wordPos[0])
        self.possesiveEnding()

        self.detectNounFromDTJJ()
        counter,newSentenceArray =0,[]

        for item in self.sentencePOS_Array:
            newWordArr = []
            newWordArr.append(self.sentenceWordsArray[counter])
            newWordArr.append(self.sentencePOS_Array[counter])

            if len(sentenceArray) > counter:        
                isIt = False
                try:
                    val = sentenceArray[counter][2]
                    isIt = True 
                except Exception, e:
                    isIt = False
                if isIt: 
                    newWordArr.append(sentenceArray[counter][2])
            # print self.sentenceWordsArray[counter]," [-] ",self.sentencePOS_Array[counter]

            newSentenceArray.append(newWordArr)
            counter = counter + 1
        counter = 0

        return newSentenceArray 
    def possesiveEnding(self):
        posArray = self.sentencePOS_Array
        for i in [i for i,x in enumerate(posArray) if x == "POS"]:
            if i > 0:
                indx = i - 1
                if self.sentenceWordsArray[i] == "'s":
                    self.sentencePOS_Array[indx] = posArray[indx]+"-NNP"
                elif self.sentenceWordsArray[i] == "'":
                    self.sentencePOS_Array[indx] = posArray[indx]+"-NNS"
                else:
                    self.sentencePOS_Array[indx] = posArray[indx]

    def detectNounFromDTJJ(self):
        posArray = self.sentencePOS_Array
        stopIndx = 0
        noun_pronoun_arr = ["NN","NNS","NNP","NNPS","PRP","PRP$"]

        for i in [i for i,x in enumerate(posArray) if x == "DT"]:
            indx = i
            if posArray[indx + 1] == "JJ":
                nextIndx = indx + 2
                if posArray[nextIndx] in noun_pronoun_arr:
                    pass
                elif posArray[nextIndx] == "JJ":
                    pword = self.sentenceWordsArray[nextIndx]
                    wordPosDic = self.wordnet_funct.detectPOSofWord(pword)
                    if wordPosDic['noun'] > 0:
                        self.sentencePOS_Array[nextIndx] = "NN"

    def extractCapitalNamedEntities(self, sentenceArray):
        pwholeWords = []

        initialPossibleTopics = self.extractConsecutiveNouns()
        for ipt in initialPossibleTopics:
            if len(ipt) > 0:
                # ipt.insert(len(ipt),"ipt")
                if len(ipt) > 0:
                    pwholeWords.insert(len(pwholeWords),ipt)

        # capwithprethe = self.prepositionThe()
        # for cpt in capwithprethe:
        #     if len(cpt) > 0:
        #         # cpt.insert(len(cpt),"cpt")
        #         if len(cpt) > 0:
        #             pwholeWords.insert(len(pwholeWords),cpt)

        # withSpanishContractions = self.extractSpanishContrations()
        # for spt in withSpanishContractions:
        #     if len(spt) > 0:
        #         # spt.insert(len(spt),"spt")
        #         if len(spt) > 0:
        #             pwholeWords.insert(len(pwholeWords),spt)

        # pwholeWords = list(helper.multi_array_exist(pwholeWords))
        # pwholeWords = helper.removeDeterminers(pwholeWords)

        # helper.url_domain_email_research(pwholeWords)
        

        return pwholeWords

    def extractConsecutiveNouns(self): 

        posArray = self.sentencePOS_Array
        wordsArray = self.sentenceWordsArray
        posArray_fixed = []

        for pos in posArray:
            posArray_fixed.insert(len(posArray_fixed),pos)

        ctr = 0
        for posnounSequence in posArray_fixed:
            if posnounSequence in self.posIndexer:

                if posnounSequence == "CC":
                    if wordsArray[ctr] == "and":
                        posArray_fixed[ctr] = "NOUN"

                elif posnounSequence == "IN":
                    if wordsArray[ctr] in ["of","for"]:
                        if wordsArray[ctr] == "for":
                            if posArray[ctr-1][0].isupper() and posArray[ctr+1][0].isupper():
                                posArray_fixed[ctr] = "NOUN"
                        else:
                            posArray_fixed[ctr] = "NOUN"
                    elif wordsArray[ctr] in self.spanish_connector:
                        posArray_fixed[ctr] = "NOUN"

                elif posnounSequence == "JJ" and posArray[ctr][0].isupper():
                    posArray_fixed[ctr] = "NOUN"

                elif posnounSequence == "DT":
                    if wordsArray[ctr] == "the" or wordsArray[ctr] == "the":
                        if wordsArray[ctr-1] in self.conjuctionsintitles:
                            if wordsArray[ctr+1][0].isupper():
                                posArray_fixed[ctr] = "NOUN"

                        if wordsArray[ctr-1].islower() and wordsArray[ctr+1][0].isupper():
                            if posArray[ctr-1] in ["of","and"]:
                                posArray_fixed[ctr] = "NOUN"
                    elif wordsArray[ctr] == "The":
                        if wordsArray[ctr+1][0].isupper():
                            posArray_fixed[ctr] = "NOUN"

                # if posnounSequence == "POS":
                #     posArray_fixed[ctr] = "NOUN"

                elif posnounSequence == "FW" and wordsArray[ctr] in self.spanish_connector:
                    posArray_fixed[ctr] = "NOUN" ;
                elif posnounSequence == "CD": 
                    posArray_fixed[ctr] = "NOUN" ;

                else:

                    if wordsArray[ctr].lower() in postItems.removeDaysoftheWeek:
                        try:
                            if wordsArray[ctr+1][0].isupper():
                                posArray_fixed[ctr] = "NOUN"
                        except Exception:
                            pass
                    else:                       

                        # print helper.isset(ctr + 1,wordsArray)
                        # print ctr + 1, len(wordsArray), wordsArray[ctr + 1]
                        if (ctr + 1) < wordsArray:
                            if len(wordsArray[ctr]) > 0:
                                if wordsArray[ctr][0].isupper():
                                    posArray_fixed[ctr] = "NOUN"
                                # elif wordsArray[ctr + 1] in self.name_suffixes:
                                #     posArray_fixed[ctr] = "NOUN"
            elif posnounSequence == "SYMBOL":
                if wordsArray[ctr] == "," and wordsArray[ctr + 1] in self.name_suffixes:
                    # print "<3 >--->",posArray_fixed[ctr], wordsArray[ctr + 1]
                    posArray_fixed[ctr] = "NOUN"
                elif wordsArray[ctr] in self.qoutationSymbols:
                    if ctr > 0 and ctr < len(wordsArray):
                        if wordsArray[ctr -1][0].isupper() and wordsArray[ctr -1][0].isupper():
                            posArray_fixed[ctr] = "NOUN"
            else:

                if ctr > 0 and ctr < len(wordsArray):
                    if wordsArray[ctr][0].isupper() and (ctr + 1) < len(wordsArray):
                        if wordsArray[ctr - 1][0].isupper():
                            posArray_fixed[ctr] = "NOUN"
                        elif wordsArray[ctr + 1][0].isupper():
                            posArray_fixed[ctr] = "NOUN"
            ctr = ctr + 1

        proper_nouns = []

        # helper.printArray(posArray_fixed)

        a= posArray_fixed
        b = range(len(a))

        qoutCount = 0

        for group in groupby(iter(b), lambda x: a[x]):
            if group[0] == "NOUN":
                lis = list(group[1])
                countr = min(lis) 
                if min(lis) < max(lis) and wordsArray[countr] != "ng":

                    pnouns = []
                    while countr <= max(lis):
                        if (countr - 1) < min(lis) and countr > 0:
                            if wordsArray[countr - 1][0].isupper() and posArray_fixed[countr - 1] == "JJ":
                                pnouns.insert(len(pnouns),wordsArray[countr - 1])

                        if wordsArray[countr][0].isupper():
                            pnouns.insert(len(pnouns),wordsArray[countr])

                        if wordsArray[countr][0].islower():
                            if posArray_fixed[countr] == "NOUN" and posArray[countr] == "IN":
                                pnouns.insert(len(pnouns),wordsArray[countr])
                            elif wordsArray[countr] == "and" and (wordsArray[countr-1][0].isupper() and wordsArray[countr+1][0].isupper()):
                                pnouns.insert(len(pnouns),wordsArray[countr])
                            if posArray_fixed[countr] == "NOUN" and posArray[countr] == "FW":
                                pnouns.insert(len(pnouns),wordsArray[countr])
                        elif wordsArray[countr] in self.qoutationSymbols:
                            pnouns.insert(len(pnouns),wordsArray[countr])
                            qoutCount = qoutCount + 1

                        elif wordsArray[countr] in self.conjuctionsintitles or posArray_fixed[countr] == "DT":
                            pnouns.insert(len(pnouns),wordsArray[countr])

                        elif posArray_fixed[countr] == "NOUN" and posArray[countr] == "CD":
                            pnouns.insert(len(pnouns),wordsArray[countr])

                        if wordsArray[countr] == "the":
                            pnouns.insert(len(pnouns),wordsArray[countr])

                        elif len(wordsArray) > countr+2:

                            if wordsArray[countr+1] == ",":
                                if wordsArray[countr+2] == "Inc.":
                                    pnouns.insert(len(pnouns),wordsArray[countr+1])
                                    pnouns.insert(len(pnouns), " ")
                                    pnouns.insert(len(pnouns),wordsArray[countr+2])
                        else:
                            pnouns.insert(len(pnouns),wordsArray[countr])
                            # print wordsArray[countr]

                        countr = countr + 1
                    if len(pnouns) > 0:
                        if pnouns[len(pnouns)-1] in self.conjuctionsintitles:
                            pnouns.pop()

                    # print pnouns

                    pnouns = helper.removeNotCapital(pnouns)
                    pnouns = helper.excessQoutation(pnouns)
                    pnouns = helper.completions(pnouns)
                    proper_nouns.insert(len(proper_nouns),pnouns)
                    pnouns = []

                elif min(lis) == max(lis):
                    pnouns = []
                    if wordsArray[min(lis)][0].isupper():
                        if min(lis) + 1 <= len(wordsArray) -1:

                            if wordsArray[min(lis) + 1] != "the":

                                if wordsArray[min(lis) + 1] not in self.conjuctionsintitles:

                                    if wordsArray[min(lis) - 1] not in self.spanish_connector and wordsArray[min(lis) + 1] not in self.spanish_connector:

                                        if posArray[min(lis) + 1] in self.stoppers:

                                            pnouns.insert(len(pnouns),wordsArray[min(lis)])
                                            pnouns = helper.removeNotCapital(pnouns)
                                            pnouns = helper.excessQoutation(pnouns)
                                            proper_nouns.insert(len(proper_nouns),pnouns)

                                            if wordsArray[min(lis) - 1] == "the":
                                                if len(pnouns) > 0:
                                                    pnouns.pop() 
                                            pnouns = []
                                        else:
                                            pnouns.insert(len(pnouns),wordsArray[min(lis)])
                                            if posArray_fixed[min(lis) + 1] == "CD":
                                                pnouns.insert(len(pnouns),wordsArray[min(lis) + 1])
                                            elif pnouns[0] in self.notallowed:
                                                pnouns.pop()
                                            elif pnouns[len(pnouns)-1] in self.conjuctionsintitles:
                                                pnouns.pop()
                                            pnouns = helper.removeNotCapital(pnouns)
                                            pnouns = helper.excessQoutation(pnouns)
                                            proper_nouns.insert(len(proper_nouns),pnouns)
                                else:

                                    if (min(lis) + 2) < len(wordsArray):
                                        if wordsArray[min(lis) + 2][0].isupper():
                                            pnouns.insert(len(pnouns),wordsArray[min(lis)])
                                            pnouns.insert(len(pnouns),wordsArray[min(lis) + 1])
                                            pnouns.insert(len(pnouns),wordsArray[min(lis) + 2])

                                            pnouns = helper.removeNotCapital(pnouns)
                                            pnouns = helper.excessQoutation(pnouns)
                                            proper_nouns.insert(len(proper_nouns),pnouns)
                            else:
                                if (min(lis) + 2) < len(wordsArray):
                                    if wordsArray[min(lis) + 2][0].isupper():
                                        pnouns.insert(len(pnouns),wordsArray[min(lis)])
                                        pnouns.insert(len(pnouns),wordsArray[min(lis)+1])
                                        pnouns.insert(len(pnouns),wordsArray[min(lis)+2])

                                        pnouns = helper.removeNotCapital(pnouns)
                                        pnouns = helper.excessQoutation(pnouns)
                                        proper_nouns.insert(len(proper_nouns),pnouns)
                    else:
                        pass
                else:
                    pass
        return proper_nouns

    def prepositionThe(self):
        pos_array   = self.sentencePOS_Array
        words_array = self.sentenceWordsArray

        nounArr =  ["NNP", "NNPS","NN","NNS","JJ"]
        pattern = []

        maxn = len(pos_array)
        for ctr in xrange(0,maxn):
            if ctr < (maxn - 3):
                if pos_array[ctr] == "DT":
                    i = ctr + 1
                    initPattern = []
                    if words_array[i][0].isupper():
                        while pos_array[i] not in self.stoppers:

                            initPattern.insert(len(initPattern),words_array[i])
                            i = i+1
                            # nounArr['']
                            if words_array[i][0].islower() and pos_array[i] in nounArr:
                                break
                            if pos_array[i] == "IN" and words_array[i] not in self.conjuctionsintitles:

                                if words_array[i] in ["by"] and pos_array[i+1] != 'DT':
                                    break
                                if pos_array[i+1] == "DT":
                                    break

                            if pos_array[i] == "SYMBOL":
                                if words_array[i] != ",":
                                    break
                        if len(initPattern) > 0:
                            if initPattern[len(initPattern)-1] in self.conjuctionsintitles:
                                initPattern.pop()
                    if len(initPattern) > 0:
                        caps = []
                        for x in xrange(0,len(initPattern)):
                            if initPattern[x][0].isupper():
                                caps.insert(len(caps),x)

                        if len(caps) == 1 and initPattern[0][0].isupper():
                            initPattern = [initPattern[0]]


                        initPattern = helper.removeNotCapital(initPattern)
                        pattern.insert(len(pattern),initPattern)

            else:
                break

        return pattern

    def extractSpanishContrations(self):
        pos_array   = self.sentencePOS_Array
        words_array = self.sentenceWordsArray
        pattern = []

        maxn = len(pos_array)
        for ctr in xrange(0,maxn):
            if ctr < (maxn - 3):
                if words_array[ctr][0].isupper():
                    initPattern = []
                    if words_array[ctr + 1] in self.spanish_connector:
                        initPattern.insert(len(initPattern), words_array[ctr])
                        initPattern.insert(len(initPattern), words_array[ctr + 1])
                        ctr = ctr + 2
                        if words_array[ctr] in self.spanish_connector_two:
                            initPattern.insert(len(initPattern), words_array[ctr + 2])
                            ctr = ctr + 1
                        initPattern.insert(len(initPattern), words_array[ctr])
                        ctr = ctr + 1

                        if len(initPattern) > ctr:
                            if words_array[ctr][0].isupper():
                                initPattern.insert(len(initPattern), words_array[ctr + ictr])
                                pattern.insert(len(pattern),initPattern)
                                break
                            else:
                                break
                        else:
                            pattern.insert(len(pattern),initPattern)
        return pattern

    def extractMonetaryValues(self, text):
        # monetary combinations
        monetary = []

        regEx = r"((([\$\£\€\P])|(?:PHP))+(\s{0,3})+(\d+(?:\d{1,}\s{1,2})?)+(\d|\.|\,\s{0,3}\d{1,}){1,})"
        result = re.findall(regEx, text)
        for x in result:
           monetary.append(x[0])

        return monetary

    def extracDigitValues(self, text):
        # monetary combinations
        digit = []

        regEx = r"((\d+(?:\d{1,}\s{1,2})?)+(\d|\.|\,\s{0,3}\d{1,}){1,})"
        result = re.findall(regEx, text)
        for x in result:
           digit.append(x[0])
        return digit

# State of the Nation








