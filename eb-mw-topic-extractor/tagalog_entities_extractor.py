# -*- coding: utf-8 -*-

import re
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import json
import postItems

from pprint import pprint
from itertools import groupby 
from package.tagsenttagalognltk import pos_tagging
import helper

tl_posTagger = pos_tagging.POS_tagger()
tagalogPOSTagdict = tl_posTagger.tlenglish_postTag()

from package.tagsenttagalognltk.trainingData import tagalog_determiners
from package.tagsenttagalognltk.trainingData import tagalog_pronouns
from package.tagsenttagalognltk.trainingData import tagalog_conjunctions
from package.tagsenttagalognltk.trainingData import tagalog_linking_verbs
from package.tagsenttagalognltk.trainingData import tagalog_modifiers
from package.tagsenttagalognltk.trainingData import tagalog_prepositions

with open('package/tagsenttagalognltk/trainingData/tagalog_colloquial.json') as data_file:
    tagalog_colloquial = json.load(data_file)

# pprint(tagalog_colloquial)

class TagalogEntitiesExtractor(object):

    text = ""
    wordpos_array = []
    tpos_list = []
    word_list = []

    tpos_list_updated = []

    tagalogDTR = tagalog_determiners.listItem
    tagalogPRO = tagalog_pronouns.listItem
    tagalogCJN = tagalog_conjunctions.listItem
    tagalogMDF = tagalog_modifiers.listItem
    tagalogPRE = tagalog_prepositions.listItem
    spanish_connector   = postItems.spanish_connector
    spanish_connector2  = postItems.spanish_connector_two
    removeDaysoftheWeek = postItems.removeDaysoftheWeek
    englishPronouns     = postItems.englishPronouns

    def __init__(self):
       return


    # """ Initialize global values                   ---
    # --- and run functions for extracting Entities  """
    def extractEntities(self,text,wordposList):

        self.text = text
        self.wordpos_array = wordposList

        for wpList in wordposList:
            self.word_list.append(wpList[0])
            self.tpos_list.append(wpList[1])

        possibleEntities = self.extractConsecutiveNouns()
        possibleEntities = self.cleanExtractedEntities(possibleEntities)

        possibleEntities = helper.removeFromTagalog(possibleEntities, "at", "end")
        possibleEntities = helper.url_domain_email_research(possibleEntities)
        possibleEntities = helper.extract_words_with_by(possibleEntities)

        return possibleEntities 

    """ Chech if nouns has connectors like [and|or|of|the|and|of|de] """
    """ if found create a new global array and save POS as XX        """
    def detectEntityConnectors(self):

        wordList = self.word_list
        wl_count = len(self.tpos_list)

        counter = 0
        for wl in self.tpos_list:

            prev_ctr1,prev_ctr2,prev_ctr3 = counter - 1,counter - 2,counter - 3
            next_ctr1,next_ctr2,next_ctr3 = counter + 1,counter + 2,counter + 3

            prev_wordEnglish = False
            next_wordEnglish = False

            try:
                if self.wordpos_array[prev_ctr1][2] == "EN":
                    prev_wordEnglish = True
            except Exception, e:
                prev_wordEnglish = False

            try:
                if self.wordpos_array[next_ctr1][2] == "EN":
                    next_wordEnglish = True
            except Exception, e:
                next_wordEnglish = False

            # """ check if word is in Capital letter"""
            if wordList[counter][0].isupper():

                if wordList[prev_ctr1] == ".":
                    if tl_posTagger.check_if_verb_from_prefixes(wordList[counter]) == True:
                        wl = "VB"

                    elif tl_posTagger.get__check_if_adjective_from_prefixes(wordList[counter]) == True:
                        wl = "ADJ" 

                self.tpos_list_updated.append("XX")

            # """ change DT before index is in IN """
            elif wl == "DT":

                if (counter < wl_count - 2 or counter > 1) and wordList[counter] in ['ang','mga','the']:
                    # ext: Samahan/Capital ng/IN mga/DT Magsasaska/
                    if self.tpos_list[prev_ctr1] == "IN" and wordList[prev_ctr2][0].isupper():
                        if  wordList[next_ctr1][0].isupper():
                            # self.tpos_list_updated.append("XX")
                            wl = "XX"

                    elif wordList[next_ctr1][0].isupper() and wordList[prev_ctr1][0].isupper():
                        wl = "XX"

                self.tpos_list_updated.append(wl)


            # """ check if wl pos is IN  """
            elif wl == "IN":
                if counter < wl_count - 2 or counter > 1:

                    if wordList[prev_ctr1][0].isupper() and wordList[next_ctr1][0].isupper():
                        wl = "XX"
                    # """ the previous word is in capital letter and the pos of next word is in DT"""
                    elif wordList[prev_ctr1][0].isupper() and self.tpos_list[next_ctr1] == "DT":
                        if wordList[next_ctr2][0].isupper():
                            wl = "XX"                            
                    else:
                        wl = wl
                    self.tpos_list_updated.append(wl)

            # """ check if wl pos is CC between two Upper case words  """
            # """ or between a Upper case word and a Determiner word  """
            elif wl == "CC":
                if counter < wl_count - 2 or counter > 1:
                    # """ the previous and next word is in capital letter  """
                    if wordList[prev_ctr1][0].isupper() and wordList[next_ctr1][0].isupper():
                        wl = "XX"

                    # """ the previous word is in capital letter and the pos of next word is in DT"""
                    elif wordList[prev_ctr1][0].isupper() and self.tpos_list[next_ctr1] == "IN":
                        if wordList[next_ctr2][0].isupper():
                            wl = "XX"
                        else:
                            wl = wl
                    else:
                        wl = wl
                    self.tpos_list_updated.append(wl)

            # """ check if wl is some kind of noun
            elif wl in postItems.posIndexerNouns:
                # """ if wl is between nound
                if self.tpos_list[prev_ctr1] == "NN" and self.tpos_list[prev_ctr1] == "NN":
                    wl = "XX"
                # """ if wl is between NN and CD(cardinal number)
                elif self.tpos_list[prev_ctr1] == "NN" and self.tpos_list[prev_ctr1] == "CD":
                    wl = "XX"
                else:
                    wl = wl
                self.tpos_list_updated.append(wl)

            elif wl == "FW":
                if wordList[counter] in postItems.spanish_connector:
                    if wordList[prev_ctr1][0].isupper() and wordList[next_ctr1][0].isupper():
                        wl = "XX"
                self.tpos_list_updated.append(wl)
            # """ cardinal numbers
            elif wl == "CD":
                if self.tpos_list[prev_ctr1] == "NN":
                    wl = "XX"
                elif self.tpos_list[prev_ctr1] == "CD":
                    wl = "XX"
                else:
                    try:
                        if self.tpos_list[next_ctr1] == "NN":
                            wl = "XX"
                    except:
                        wl = wl
                self.tpos_list_updated.append(wl)
            else:
                if wl == "SYMBOL":
                    if wordList[counter] == ",":
                        try:
                            if wordList[next_ctr1]+"." in postItems.name_suffixes:
                             wl = "XX"
                        except:
                            wl = wl
                        try:
                            if wordList[next_ctr1] in postItems.name_suffixes:
                             wl = "XX"
                        except:
                            wl = wl 
                    elif wordList[counter] == ".": 
                        try:
                            if wordList[prev_ctr1]+"." in postItems.name_suffixes:
                             wl = "XX"
                        except:
                            wl = wl 
                else:
                    if wordList[counter][0].isupper():
                        wl = "XX"
                        

                self.tpos_list_updated.append(wl)

            counter = counter + 1

        counter = 0
        # for xtlu in self.tpos_list_updated:
        #     print xtlu,wordList[counter],self.tpos_list[counter]
        #     counter = counter + 1

    """ Using regular expression, extract persons names"""
    def extractConsecutiveNouns(self):

        possibleEntities = []

        self.detectEntityConnectors()

        a = self.tpos_list_updated
        b = range(len(a))

        nameIndexes = []

        for group in groupby(iter(b), lambda x: a[x]):
            if group[0] == "XX":

                lis = list(group[1])
                nameIndexes.append(lis)

        counter = 0
        for xtlu in nameIndexes:
            wordl = []
            if len(xtlu): 
                for ind in xtlu:
                    try:
                        wordl.append(self.word_list[ind])
                    except:
                        pass

            possibleEntities.append(wordl)
            counter = counter + 1

        return possibleEntities

    def cleanExtractedEntities(self,entitiesList):

        counter = 0

        newEntities = []


        for _wordpos in entitiesList:

            if len(_wordpos) == 1:

                if _wordpos[0][0].isupper():
                    allDTs =  ["And","and",'The','the','A','an','a','An']
                    if _wordpos[0].lower() in self.tagalogDTR or _wordpos[0].lower() in allDTs:
                        pass
                    elif _wordpos[0].lower() in self.tagalogPRO:
                        pass
                    elif _wordpos[0].lower() in self.tagalogCJN:
                        pass
                    elif _wordpos[0].lower() in self.tagalogMDF:
                        pass
                    elif _wordpos[0].lower() in self.tagalogPRE:
                        pass
                    elif _wordpos[0].lower() in self.englishPronouns:
                        pass
                    else:
                        if tl_posTagger.check_if_verb_from_prefixes(_wordpos[0]) == False:

                            _iscolloquial = False
                            try:
                                tagalog_colloquial[_wordpos[0]]
                                _iscolloquial = True
                            except Exception, e:
                                _iscolloquial = False
                            if _iscolloquial == False:
                                if _wordpos[0].lower() in self.removeDaysoftheWeek:
                                    pass
                                else:
                                    newEntities.append(_wordpos)
                            else:
                                pass
                        else:
                            pass

            else:
                # search group of words that forms a title with of, and and the
                intersection = set(_wordpos).intersection(["of","and","the"])

                # if group is found
                if len(intersection) > 0:
                    try:
                        ng_index = _wordpos.index("ng");
                    except Exception, e:
                        ng_index = -1

                    if ng_index > -1:
                        item = [];
                        for x in xrange(0,len(_wordpos)):
                            if x == ng_index:
                                newEntities.append(item);
                                item = []
                            elif x == 0:
                                if _wordpos[x].lower() in self.tagalogDTR or _wordpos[x].lower() in ["And","and"]:
                                    pass
                                elif _wordpos[x].lower() in self.tagalogPRO:
                                    pass
                                elif _wordpos[x].lower() in self.tagalogCJN:
                                    pass
                                elif _wordpos[x].lower() in self.tagalogMDF:
                                    pass
                                elif _wordpos[x].lower() in self.tagalogPRE:
                                    pass
                                else:
                                    item.append(_wordpos[x])
                            else:
                                item.append(_wordpos[x])

                        newEntities.append(item)
                    else:
                        _wordpos,entitiesList = self.wordpos_popper(counter, _wordpos, entitiesList)
                        newEntities.append(_wordpos);
                else:
                    _wordpos,entitiesList = self.wordpos_popper(counter, _wordpos, entitiesList)
                    newEntities.append(_wordpos);
            counter = counter + 1

        return newEntities 


    def wordpos_popper(self, counter, _wordpos, entitiesList):
        try:      
            if _wordpos[0].lower() in self.tagalogDTR or _wordpos[0].lower() in ["And","and"]:
                entitiesList[counter].pop(0);
            elif _wordpos[0].lower() in self.tagalogPRO:
                entitiesList[counter].pop(0);
            elif _wordpos[0].lower() in self.tagalogCJN:
                entitiesList[counter].pop(0);
            elif _wordpos[0].lower() in self.tagalogMDF:
                entitiesList[counter].pop(0);
            elif _wordpos[0].lower() in self.tagalogPRE:
                entitiesList[counter].pop(0);
        except:
            pass

        return _wordpos,entitiesList
