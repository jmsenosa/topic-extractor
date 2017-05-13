# -*- coding: utf-8 -*-

import re
from nltk.util import ngrams

from trainingData import tagalog_conjunctions
from trainingData import tagalog_determiners
from trainingData import tagalog_linking_verbs
from trainingData import tagalog_modifiers
from trainingData import tagalog_prepositions
from trainingData import tagalog_pronouns
from trainingData import tagalog_stoppers

from nltk import word_tokenize
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import os

"""
this module is used primarily for POS tagging
it follows some of the algorithms used in TPOST;
however this is not feature based, but rather uses a large dictionary
"""
class POS_tagger():

    #text file directory that contains alot of filipino words and its tags
    __word_list_dir = os.path.abspath("package/tagsenttagalognltk/preDefinedFeatures/wordtags.txt")

    #text file directory that contains the sentences tags
    #rather than words, it is the corresponding tags in the file
    __pos_tag_pattern_dir = os.path.abspath("package/tagsenttagalognltk/trainingData/sentences_tags.txt")

    #text file directory that contains the patterns extracted from the sentences tags
    #patterns are merely 5-gram pos tags
    # __pos_tag_pattern_outputs_dir = os.path.abspath("package/tagsenttagalognltk/outputs/pos_tag_patterns_5grams.txt")

    #contains the list for the following predefined words
    __list_of_determiners   = tagalog_determiners.listItem
    __list_of_pronouns      = tagalog_pronouns.listItem
    __list_of_conjunctions  = tagalog_conjunctions.listItem
    __list_of_stoppers      = tagalog_stoppers.listItem
    __list_of_linking_verbs = tagalog_linking_verbs.listItem
    __list_of_prepositions  = tagalog_prepositions.listItem
    __list_of_modifiers     = tagalog_modifiers.listItem
    __list_of_articles      = ["ang","Ang"]

    #these patterns are usually seen as adjectives
    #the basis are its affixes
    __adjective_patterns = [
        "pang[A-Za-z]+",
        "pam[A-Za-z]+",
        "pa[^g][A-Za-z]+",
        "nakaka[A-Za-z]+",
        "nakapagpapa[A-Za-z]+",
        "napaka[A-Za-z]+",
        "ma[A-Za-z]+",
        "naka[A-Za-z]+",
        "maka[A-Za-z]+"
        ]

    #verbs
    __verb_patterns = [
        "nag|Nag\-{0,1}[A-Za-z]+", #(ipinag|Ipinag)[A-Za-z]
        "mag|Mag\-{0,1}[A-Za-z]+",
        "pa|Pa\-{0,1}[A-Za-z]+?in",
        "pag|Pag\-{0,1}[A-Za-z]+?in+",
        "ma|Ma\-{0,1}[A-Za-z]+",
        "na|Na\-{0,1}[A-Za-z]+",
        "nana|Nana\-{0,1}[A-Za-z]+",
        "ipa|Ipa\-{0,1}[A-Za-z]+",
        "ipina|Ipina\-{0,1}[A-Za-z]+",
        "ipag|ipag\-{0,1}[A-Za-z]+",
        "ipinag|Ipinag\-{0,1}[A-Za-z]+",
        "maki|Maki\-{0,1}[A-Za-z]+",
        "naki|Naki\-{0,1}[A-Za-z]+",
        "makiki|Makiki\-{0,1}[A-Za-z]+",
        "nakiki|Nakiki\-{0,1}[A-Za-z]+",
        "makikipag|Makikipag\-{0,1}[A-Za-z]+",
        "nakikipag|Nakikipag\-{0,1}[A-Za-z]+",
        "mapa|Mapa\-{0,1}[A-Za-z]+",
        "napa|Napa\-{0,1}[A-Za-z]+",
        "mapapa|Mapapa\-{0,1}[A-Za-z]+",
        "napapa|Napapa\-{0,1}[A-Za-z]+",
        "magka|Magka\-{0,1}[A-Za-z]+",
        "nagka|Nagka\-{0,1}[A-Za-z]+",
        "magkaka|Magkaka\-{0,1}[A-Za-z]+",
        "nagkaka|Nagkaka\-{0,1}[A-Za-z]+",

        "magsi|Magsi\-{0,1}[A-Za-z]+",
        "nagsi|Nagsi\-{0,1}[A-Za-z]+",
        "magsisi|Magsisi\-{0,1}[A-Za-z]+",
        "nagsisi|Nagsisi\-{0,1}[A-Za-z]+",
        "sinu|Sinu\-{0,1}[A-Za-z]+?an",
        "sina|Sina\-{0,1}[A-Za-z]+?an",
        "maka|Maka\-{0,1}[A-Za-z]+",
        "naka|Naka\-{0,1}[A-Za-z]+",
        "makaka|Makaka\-{0,1}[A-Za-z]+",
        "nakaka|Nakaka\-{0,1}[A-Za-z]+",
        "makaka|Makaka\-{0,1}[A-Za-z]+",
        "nakaka|Nakaka\-{0,1}[A-Za-z]+",
        "itina|Itina\-{0,1}[A-Za-z]+",
        "Um|um\-{0,1}[A-Za-z]",

        "maka|Maka\-{0,1}[A-Za-z]+",
        "naka|Naka\-{0,1}[A-Za-z]+",
        "makaka|Makaka\-{0,1}[A-Za-z]+",
        "nakaka|Nakaka\-{0,1}[A-Za-z]+",
        "makaka|Makaka\-{0,1}[A-Za-z]+",
        "nakaka|Nakaka\-{0,1}[A-Za-z]+",
        "Um|um\-{0,1}[A-Za-z]",

        "[A-Za-z]+?in",
        "[A-Za-z]+?an",
        "[A-Za-z]{1}um[A-Za-z]+",
        "[A-Za-z]{1}in[A-Za-z]+"
        ]

    #the data for pos tags is in a very specified one
    #these are the conversion for each tag
    __convert_tags = {
        "N":["NN","NNC","NNP","NNPA"],
        "PR":["PR","PRS","PRSP","PRO","PROP","PRQ","PRL","PRN","PRC","PRF"],
        "PREP":["PPO","PPTS","PPIN","PPU","PPM","PPA"],
        "CONJ":["CC","CCA","CCD","CCC","CCP"],
        "V":["VB","VBW","VBS","VBH","VBTS","VBTR","VBTF"],
        "ADJ":["JJ","JJD","JJC","JJCC","JJCS","JJCN","JJN"],
        "ADV":["RB","RBD","RBN","RBC","RBQ","RBT","RBF","RBW","RBI","RBM"],
        "CD": ["CD","CDB"],
        "STOPPER": ["PM","PMP","PME","PMQ","PMC","PMS"],
        "DT":["DTCP","DTC"],
        "VBL":["VBL"]
        }

    #holds all the 5gram patterns to be extracted from the text file earlier
    __pos_tag_patterns_5grams = {}
    __pos_tag_patterns_3grams = {}

    #holds all the dictionary-based pos tags for each words
    __words_postag_dict = {}



    def __init__(self):

        #train the model
        self.train_lookup()
        self.train_pos_tag_patterns()

    """
    this method is used to train the model of its lookup feature
    no parameters as it uses the attribute __word_list_dir
    """
    def train_lookup(self):

        #open up the text file and store it in the contents variable
        fsreader = open(self.__word_list_dir,"r")
        contents= fsreader.readlines()
        fsreader.close()

        #fill in the lookup dictionary
        for entry in contents:

            #remove all newline markers
            entry = entry.replace("\n","")

            #each entry is seperated by ":"
            temp = entry.split(" : ")

            #check if the word is not yet in the word tags list
            if temp[0] not in self.__words_postag_dict:

                #fill in the dictionary with the word as the key, and its pos tag[s] as the value
                self.__words_postag_dict[temp[0]] = temp[1].split(",")

            #if the word is already in the list
            else:
                tags = temp[1].split(",")
                #just add it in the current value
                for tag in tags:
                    self.__words_postag_dict[temp[0]].append(tag)

    """
    this method is used to train the pos tagger of the pos tag patterns/templates (5grams)
    no paremeters as it uses the class attribute __pos_tag_pattern_dir
    """
    def train_pos_tag_patterns(self): 

        return True
    """
    this method is the lookup feature of this pos tagger; it labels each of the words of a given text
    the text should however be grammatically perfect
    parameters -
    sentence: string, the text you want to be tagged
    """
    def lookup_label(self,sentence):

        #remove of unnecessary whitespace
        sentence = sentence.strip()

        #split all the words from the sentence by using the spaces
        # words = sentence.split(" ")
        words = word_tokenize(sentence.encode('utf-8'))

        #initialize the list that would contain the output
        output = []

        #loop through all the words
        for i in range(len(words)):
            # print words[i]
            #lower case the word if it is the starting word
            if (i==0):
                words[0] = words[0].lower()

            #this part should error if the word cannot be found from the words list
            try:
                #use the lookup method to see what is the pos tag of the current word [i]
                pos = self.lookup(words[i])

                #if the tags is only 1
                if(len(pos) == 1):

                    #add the tag to the output
                    output.append([words[i],pos[0]])

                #if the tags is more than 1, then mark it as ambiguous
                elif(len(pos) > 1):
                    output.append([words[i],"AMB"])

            #if it errors due to not found index, then do this
            except:


                #check if the word is an adjective depending from its affixes
                if self.__check_if_adjective_from_prefixes(words[i]):
                    output.append([words[i],"ADJ"])

                #if the first test fails, check if it is a verb again, based form its affixes
                elif self.__check_if_verb_from_prefixes(words[i]):
                    output.append([words[i],"V"])

                #if all else fails
                else:
                    #if the starting letter is capital, then it is a noun
                    if i > 0 and words[i][0].isupper():
                        output.append([words[i],"N"])

                    #give up, it is unknown
                    else:
                        output.append([words[i],"UNK"])
        #return the output list
        return output

    """
    this method is used to solve the ambiguous and unknown tags by using the 5gram patterns
    it checks the neigboring words of their pos tags ... example, the labeled sentence contains
    [ ADJ ADV UNK N N ] this method would look for a template/pattern that has also an ADJ ADV and N N as its neigbors
    parameters -
    labeled_sentence: a 2d array that contains the words with their corresponding pos tags
    """
    def pattern_label(self, labeled_sentence):
        index = 0

        #loop through all word + tags, find ambiguous or unknown words
        for word_tag in labeled_sentence:

            #if the pos tag of the word is unknown or ambiguous
            if word_tag[1] == "UNK" or word_tag[1] == "AMB":

                #initialize the list to get the pattern
                pattern = []

                #if the index of the word from the list is less than 4 (the word is no more than the fifth in the sentence)
                if index <= 4:

                    #get the first five tags in the list
                    pattern = [words[1] for words in labeled_sentence[:5]]

                    #if the word is ambiguous, use the method for ambiguous
                    if word_tag[1] == "AMB":
                        word_tag[1] = self.get_possible_pattern_amb(pattern,index,self.lookup(word_tag[0]))
                    else:
                        word_tag[1] = self.get_possible_pattern(pattern,index)

                #if the word is not in the first five words, but still not at the last three words
                elif index > 4 and index+2 <len(labeled_sentence):

                    #get the two neighboring tags
                    pattern = [words[1] for words in labeled_sentence[index-2:index+3]]

                    #if the word is ambiguous, use the method for ambiguous
                    if word_tag[1] == "AMB":
                        word_tag[1] = self.get_possible_pattern_amb(pattern,index,self.lookup(word_tag[0]))
                    else:
                        word_tag[1] = self.get_possible_pattern(pattern,index)

                #if the word is in the last 3 words of the sentence
                else:
                    pattern = [words[1] for words in labeled_sentence[-5:]]
                    # print word_tag[0], index, len(labeled_sentence)
                    word_tag[1] = self.get_possible_pattern(pattern,5 - (len(labeled_sentence) - index))


            index += 1

        #return the modified labeled sentence
        return labeled_sentence


    """
    this is method is the main method to predict sentences; it uses both lookup and template/pattern methods
    parameter-
    sentence: string
    """
    def predict(self,sentence):
        lookup = self.lookup_label(sentence)
        pattern_find  = self.pattern_label(lookup)
        return pattern_find

    """
    this method just lookups through all the lexicons available for its corresponding pos tags
    parameter -
    word: string
    """
    def lookup(self,word):

        #checks the the predefined list of whether the word is one of them
        if word in self.__list_of_pronouns:
            return ["PR"]
        elif word in self.__list_of_conjunctions:
            return ["CONJ"]
        elif word in self.__list_of_stoppers:
            return ["STOPPER"]
        elif word in self.__list_of_determiners:
            return ["DT"]
        elif word in self.__list_of_stoppers:
            return ["STOPPER"]
        elif word in self.__list_of_linking_verbs:
            return ["VBL"]
        elif word in self.__list_of_prepositions:
            return ["PREP"]
        elif word in self.__list_of_modifiers:
            return ["ADV"]
        elif word in self.__list_of_articles:
            return ["ART"]
        #check the dictionary of the word, it would error if it cannot be found
        try:
            return list(set([tag.strip() for tag in self.__words_postag_dict[word]]))
        except:
            #give up
            return None


    #------- utility methods -------------#

    """
    method used to check whether a string follows a regex
    """
    def __regex_find(self,regex,string):
        q = re.findall(regex,string)
        if len(q) == 0 or q == None:
            return False
        return len(q[0]) == len(string)

    """
    use the regexes from the verb affix patterns to check the tag of the word
    """
    def __check_if_verb_from_prefixes(self,word):
        for pattern in self.__verb_patterns:
            if self.__regex_find(pattern,word):
                return True
        if word[0:2] == word[2:4]:
            return True
        return False

    def check_if_verb_from_prefixes(self,word):
        for pattern in self.__verb_patterns:
            if self.__regex_find(pattern,word):
                newword = "";
                if pattern == "[A-Za-z]{1}um[A-Za-z]+":
                    newword = word.replace('um', '', 1);
                elif pattern == "[A-Za-z]{1}in[A-Za-z]+":
                    newword = word.replace('in', '', 1);
                else:
                    return True

                if newword != "":

                    found = False
                    wordCheck = []
                    try:
                        wordCheck = self.__words_postag_dict[word.lower()]
                        if wordCheck.count('v') > 0:
                            return True
                        else:
                            found = False
                    except:
                        found = False

                    if found == False:
                        try:
                            wordCheck = self.__words_postag_dict[newword.lower()]
                            return True
                        except:
                            return False
                    else:
                        return False



        if word[0:2] == word[2:4]:
            return True
        return False


    """
    use the regexes from the adjective affix patterns to check the tag of the word
    """
    def __check_if_adjective_from_prefixes(self,word):
        if (not word.startswith("ma")) and word.endswith("in"):
            return False

        for pattern in self.__adjective_patterns:
            if self.__regex_find(pattern,word):
                return True
        return False

    def get__check_if_adjective_from_prefixes(self,word):
        if (not word.startswith("ma")) and word.endswith("in"):
            return False

        for pattern in self.__adjective_patterns:
            if self.__regex_find(pattern,word):
                return True
        return False

    """
    this method is the one that checks for the possible pattern of a 5 gram
    parameters -
    input_pattern: list containg word+tags
    """
    def check_for_patterns(self,input_pattern,grams):

        #initialize a list that contains the possible patterns for the unknown pos tag word
        possibles = []

        #if the ngrams specified are 5, use the 5gram dict, use 3grams otherwise
        patterns = None
        maxScore = None
        if grams == 5:
            patterns = self.__pos_tag_patterns_5grams.keys()
            maxScore = 5
        elif grams == 3:
            patterns = self.__pos_tag_patterns_3grams.keys()
            maxScore = 3

        #loop through all the patterns stored in __pos_tag_patterns
        for template in patterns:

            #length of the input_pattern
            pat_length = len(input_pattern)

            #convert the string template to a tuple
            template = eval(template)

            #if the pattern is 5gram, then its initial score is 5
            if pat_length > 4:
                score = maxScore

            #else, its initial score would equal to its length
            else:
                score = pat_length

            #loops through the pattern and matches the input_pattern to the template elment by element
            #each mismatched element would decrease the score for that template
            for index in range(pat_length):
                try:
                    if input_pattern[index] == template[index]:
                        pass
                    else:
                        score -= 1
                except IndexError:
                    pass

            #the template would pass if the score is greater than or equal to 4  and it is either a  4gram or 5gram
            if score >= maxScore-1 and pat_length>3:
                possibles.append(template)
            #supporsts 3grams
            elif score == pat_length-1 and pat_length>=3:
                possibles.append(template)

        return possibles


    #method to determine the highest occuring pattern
    def getHighestPattern(self,patterns,grams):
        highest = []
        #use the corresponding dictionary
        if grams == 5: source = self.__pos_tag_patterns_5grams
        elif grams == 3: source = self.__pos_tag_patterns_3grams

        if len(patterns)>0:
            #get the highest occuring pattern
            highest = patterns[0]
        for item in patterns:
            if source['highest'] < source['item']:
                highest = item
        return highest

    def searchUNK_or_AMB(self,pattern):
        index =0
        for item in pattern:
            if item == "UNK" or item == "AMB" or item =="unk" or item=="amb":
                return index
            index += 1
        return None



    """
    get a single possible pos tag from a list of possible patterns
    parameters:
    pattern: pattern of pos tags; ex: [ADJ N UNK PREP N]
    index: position of the pattern in the sentence
    returns a pos tag string
    """
    def get_possible_pattern(self,pattern,index):
        # print pattern, index
        #if the position of the word in the pattern is less or the fourth one
        if index <= 4 and type(index) is int:


            #print "CHECKING 5-GRAM:" +`pattern`

            #get the highest occurence of a possible pattern, then return the pos tag found
            possibles = self.check_for_patterns(pattern,5)
            #print "POSSIBLE 5-GRAMS"+`possibles`

            answer = self.getHighestPattern(possibles,5)
            if len(answer)>0:
                return answer[self.searchUNK_or_AMB(pattern)]

            #if the 5gram fails use the 3gram
            #crop the 5gram to be trigram
            if self.searchUNK_or_AMB(pattern) == len(pattern) - 1 and len(pattern) >= 3:
                pattern_for_trigram = pattern[len(pattern)-3:]
            elif self.searchUNK_or_AMB(pattern) == 0:
                pattern_for_trigram = pattern[0:3]
            elif self.searchUNK_or_AMB(pattern) == 1:
                pattern_for_trigram = pattern[0] + pattern[1] + ( pattern[2] if len(pattern)>=3 else [])
            elif self.searchUNK_or_AMB(pattern) == 2:
                pattern_for_trigram = [pattern[0]] + [pattern[1]] + [pattern[2]]
            elif self.searchUNK_or_AMB(pattern) == 3:
                pattern_for_trigram = [pattern[2]] + [pattern[3]] +[pattern[4]]
            #print "CHECKING 3-GRAM:" + `pattern_for_trigram`

            #answer searchs
            possibles = self.check_for_patterns(pattern_for_trigram,3)

            #print "POSSIBLE 3-GRAMS"+`possibles`
            answer = self.getHighestPattern(possibles,3)
            if len(answer)>0:
                return answer[self.searchUNK_or_AMB(pattern_for_trigram)]

            #give up
            return "UNK"

        #if the position of the word is greater or the third one
        elif index >= 3 and type(index) is int:

            #print pattern
            #get the highest occurence of a possible pattern, then return the pos tag found
            possibles = self.check_for_patterns(pattern,5)

            answer = self.getHighestPattern(possibles,5)
            if len(answer)>0:
                return answer[self.searchUNK_or_AMB(pattern)]

            #crop the 5gram to be trigram
            if self.searchUNK_or_AMB(pattern) == len(pattern) - 1 and len(pattern) >= 3:
                pattern_for_trigram = pattern[len(pattern)-3:]
            else:
                index_of_interest= self.searchUNK_or_AMB(pattern)
                pattern_for_trigram =  [pattern[index_of_interest-1]] + [pattern[index_of_interest]] + [pattern[index_of_interest+1]]
            #print pattern_for_trigram
            #answer searchs
            possibles = self.check_for_patterns(pattern_for_trigram,3)
            answer = self.getHighestPattern(possibles,3)
            if len(answer)>0:
                return answer[self.searchUNK_or_AMB(pattern_for_trigram)]

            #give up
            return "UNK"

        return "UNK"


    """
    get a single possible pos tag from a list of possible patterns; this is seperated from the
    other method because the pos tag that would be needed to be extracted should be in the choices
    of the ambiguous word
    parameters:
    pattern: pattern of pos tags; ex: [ADJ N UNK PREP N]
    index: position of the pattern in the sentence
    choices: the pos tags that are possibly the tag of the word
    returns a pos tag string
    """
    def get_possible_pattern_amb(self,pattern,index,choices):
        return self.get_possible_pattern(pattern,index)

    """
    translates the specific pos tags to a broader format
    """
    def __convert_pos_tag(self,pos_tag):
        # for key in self.__convert_tags.keys():
        #     if pos_tag in self.__convert_tags[key]:
        #         return key
        # if pos_tag.startswith("DT"):
        #     return "dt"
        # elif pos_tag.startswith("PP"):
        #     return "prep"
        return pos_tag

    """
    converts all the pos tags of a given text
    """
    def __convert_pos_tags_of_a_line(self,line):
        splitted_line = line.split(" ")
        converted = []
        for word in splitted_line:
            converted.append(self.__convert_pos_tag(word))

        return converted

    def extract(self, text):

        newItem = []

        pos_tagged = self.predict(text)
        for taggedWord in pos_tagged:

            pos = taggedWord[len(taggedWord)-1].upper()

            newTagged = []
            newTagged.append(taggedWord[0])
            newTagged.append(pos)

            newItem.append(newTagged)

        return newItem

    def tlenglish_postTag(self):
        return self.__words_postag_dict
# text = "MANILA, Philippines – Bawal na ang hindi pagsusukli ng tama sa mga consumers o mamimili kahit gaano pa kaliit ang sukli nito. Ito'y matapos aprubahan ng Bicameral Conference Committee ang panukalang batas nina Las Piñas City Rep. Mark Villar, chairman ng House Committee on Trade and Industry at Sen. Bam Aquino, chairman ng Senate Committee on Trade, Commerce and Entrepreneurship. Ang House bill 4730 at Senate bill 1618 ay inaprubahan ng naturang komite na naglalayong maprotektahan ang mga consumer mula sa unfair trade practices. Nakapaloob din sa panukala ang pag-aatas sa mga business establishments na maglagay ng price tags, kung saan nakalagay ang eksaktong retail price per unit o service. Bukod dito kailangan din ilagay ang naturang price tag sa mga lugar na makikita agad ng consumers. Itinatakda ng panukala ang pagmumulta ng P500 hanggang P25, 000 o 3%-10% ng gross sales ng business establishment, kung alinman ang mas mataas; at suspension o pagbawi sa license to operate sa ilang ulit na opensa ang ipapataw sa mga lalabag na establisimiyento. Sinuportahan ng Department of Trade and Industry (DTI) at Bangko Sentral ng Pilipinas (BSP) ang pagpasa sa naturang panukala. \"This will avoid misleading the consumer as to the exact price they have to pay for the goods or services and consequently, the exact change due them,\" ayon kay Villar. Inihain ng kongresista ang nasabing panukala bilang tugon sa mga reklamo ng mga mamimili partikular na sa mga malala­king mall at establisimyento sa bansa na hindi nagbibigay ng tamang sukli. Sa halip na tamang sukli ay nagbibigay na lamang ang mga ito ng maliliit na bagay o kendi dahil sa katwiran na mayroong \"coin shortage\" o mahirap makakuha ng barya mula sa mga banko."
# x = POS_tagger()
# newitems = x.index(text)
# for newitem in newitems:
#     print newitem