# -*- coding: utf-8 -*-
import re
import named_entity_recognizer
nameentityrecognizer = named_entity_recognizer.NameEntityRecognizer()

def isset(value,array):
    if value < len(array):
        return True
    else:
        return False


def multi_array_exist(array):
    found = set()
    for item in array:
        if item[0] not in found:
            yield item
            found.add(item[0])

def printArray(array):
    for arr in array:
        print arr

def printArrayDoble(array1,array2):
    for x in xrange(0,len(array1)):
        print array1[x]," ",array2[x]

def removeDeterminers(pwholeWords):
    determinerList = ["the","some","this","a","my","an","The","Some","This","A","My","An","THE"]
    if len(pwholeWords) > 0:
        for x in xrange(0,len(pwholeWords)-1):
            if len(pwholeWords[x]) > 0:
                # print pwholeWords[x],"sexy"
                initIndex = 0
                finalIndex = len(pwholeWords[x]) - 1

                if pwholeWords[x][initIndex] in determinerList:
                    pwholeWords[x].pop(initIndex)
                if pwholeWords[x][finalIndex] in determinerList:
                    pwholeWords[x].pop(finalIndex)

    return pwholeWords

def removeNotCapital(words):
    determinerList = ["from","at","as","but","the","some","this","a","my","an","Some","This","A","My","An","Did","THE","of","Of","If","if","In","in","on","at","both","Both","and","And","Because","because","These","for","For"]
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Lunes","Martes","Miyerkules","Huwebes","Biyernes","Sabado","Linggo"]
    if len(words) > 0:
        if len(words) == 1:
            if words[0] in determinerList or words[0] in days:
                words.pop()
            elif ddweek(words[0]):
                words.pop()
            elif _isemail(words[0]):
                words.pop()
        else:
            lastIndex = len(words) - 1

            if words[lastIndex] in determinerList:
                words.pop()
            if words[0] in determinerList:
                words.pop(0)

            if len(words) > 0:
                if words[0] in determinerList:
                    words.pop(0)
    return words


def ddweek(word):
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Lunes","Martes","Miyerkules","Huwebes","Biyernes","Sabado","Linggo"]

    if word in (day.upper() for day in days):
        return True
    else:
        return False

def _isemail(word):
    if word.find("@") == -1:
        return False
    else:
        return True

def validateEmail(email):

    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

name_suffixes = ["B.V.M.", "CFRE", "CLU", "CPA", "C.S.C.", "C.S.J.", "D.C.", "D.D.", "D.D.S.", "D.M.D.", "D.O.", "D.V.M.", "Ed.D.", "Esq.", "II", "III", "IV", "Inc.", "J.D.", "Jr.", "LL.D.", "Ltd.", "M.D.", "O.D.", "O.S.B.", "P.C.", "P.E.", "Ph.D.", "Ret.", "R.G.S", "R.N.", "R.N.C.", "S.H.C.J.", "S.J.", "S.N.J.M.", "Sr.", "S.S.M.O.", "MA", "MBA", "MS", "MSW"]
def completions(wordList):
    # print "I believe in the thing called love: ",wordList
    # print name_suffixes

    for x in xrange(0,len(wordList)):
        if wordList[x] in name_suffixes:
            currcount = x
            prevWord = wordList[currcount-1]

            if prevWord != ",":
                wordList.insert( x, " ")
                wordList.insert( x, ", ")
                break


    return wordList

def excessQoutation(wordArrays):

    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    singleQouteStorage = []
    doubleQouteStorage = []

    lastIndex = len(wordArrays) - 1

    singleQoutationSymbol = ["'","‘","’","'"]
    doubleQoutationSymbol = ['"',"``","“","”", "''"]

    for x in xrange(0,len(wordArrays)):
        if wordArrays[x] in singleQoutationSymbol:
            singleQouteStorage.insert(len(singleQouteStorage),x)

        if wordArrays[x] in doubleQoutationSymbol:
            doubleQouteStorage.insert(len(doubleQouteStorage),x)

    qouteTest = ""

    if len(doubleQouteStorage) == 1 and len(singleQouteStorage) == 0:
        wordArrays = oneQoutesFound(doubleQouteStorage, wordArrays)
    elif len(doubleQouteStorage) == 0 and len(singleQouteStorage) == 1:
        wordArrays = oneQoutesFound(singleQouteStorage, wordArrays)
    else:
        pass
    return wordArrays

def oneQoutesFound(qouteStorage, wordArrays):

    ctr = 0
    newArrayOfWords = []
    indCtr = qouteStorage[0]

    while ctr < indCtr:
        nawCtr = len(newArrayOfWords)
        word = wordArrays[ctr]
        newArrayOfWords.insert(nawCtr, word)
        ctr = ctr + 1

    return newArrayOfWords

def regex_find(regex,string):
        q = re.findall(regex,string)
        if len(q) > 0:
            return True
        return False

def extract_words_with_by(listOfWords):
    
    ctr = 0

    search_array  = []
    storage_array = []
    
    for wordlist in listOfWords:
        byindexes = [];
        lastIndex = len(wordlist) - 1

        if "by" in wordlist:
            byindexes.append(wordlist.index("by"))
        if "By" in wordlist:
            byindexes.append(wordlist.index("By"))
        if "BY" in wordlist:
            byindexes.append(wordlist.index("BY"))
        
        # byindexes.reverse()

        if len(byindexes) == 1:
            x = byindexes[0]
            if x == 0 or x == lastIndex:
                listOfWords[ctr].pop(x)
        else:    
            subtractor = 0;
            for x in byindexes:
                if x == 0:
                    listOfWords[ctr].pop(x)
                    subtractor = 1 
                if x == lastIndex:
                    listOfWords[ctr].pop(x)
                if x > 0 and x <= lastIndex:  
                    if subtractor == 1:
                        x = x - subtractor
                    prev_word = listOfWords[ctr][x-1]
                    if prev_word.lower() == "photo":
                        listOfWords[ctr].pop(x-1) 
                        storage_array.append(ctr)

                        new_list = [item.lower() for item in listOfWords[ctr]]
                        new_index = new_list.index('BY'.lower()) 
                        search_array.append(new_index)
        ctr = ctr + 1

    storage_array.reverse()        
    for x in xrange(0,len(storage_array)):

        words = " ".join(listOfWords[storage_array[x]])
        words = words.strip() 
        words = words.split(listOfWords[storage_array[x]][search_array[x]])



        counter = storage_array[x]
        listOfWords.pop(storage_array[x]) 

        for word in words: 
            new_str = []
            xwordlist = word.split(" ")

            for word in xwordlist:
                if word != "":
                    new_str.append(word)

            listOfWords.insert(counter,new_str)
            counter = counter + 1 

    return listOfWords
def url_domain_email_research(listOfWords):
    re_list = [
        "((?:http|http)+([\:](\/\/)){0,1})(^www$){0,1}([a-zA-Z-_]*)(\.[a-z]+){0,2}", #website url
        "([a-zA-Z]*\.+[a-zA-Z]+([a-zA-Z]*)+(\.+[a-zA-Z]*){0,2})", #website domain name
        "/^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$/" #email
    ]

    itemIndex = []

    for x in xrange(0,len(listOfWords)-1): 
        word = " ".join(listOfWords[x]) 
        for pattern in re_list:
            if regex_find(pattern,word):
                itemIndex.append(x) 
        
    if len(itemIndex) > 0:
        itemIndex.reverse()

        for indx in itemIndex:
            listOfWords.pop(indx)

    return listOfWords



def removeFromTagalog(listOfWords, something, position):
    counter = 0
    for x in xrange(0,len(listOfWords)-1): 

        total = len(listOfWords[x])

        if position == "end":
            lastIndex = total-1
            try:
                if listOfWords[x][lastIndex] == something:
                    listOfWords[x].pop(lastIndex)
            except:
                pass
    return listOfWords
