#coding=utf-8


'''
 This program finds acronym inside the text article.

 One instance of an acronym is it could be inside of a parentheses. eg: "Official Development Assistance (ODA)"

'''


from wordfeatures import getpos
from nltk.tokenize import word_tokenize

def checkifsameletter(acronym):
    #checks if acronym is same letter (eg: PPP)
    ch = {}
    y = list(acronym)
    for i in y:
        try:
            ch[i] = ch[i] + 1
        except KeyError:
            ch[i] = 1

    if len(ch) == 1 and ch[acronym[0]] == len(acronym):
        # print acronym, "> True"
        return True
    else:
        # print acronym, "> False"
        return False

def checkifrecurringletter(acronym):
    #check if acronym has recurring letter like SWS
    ch = {}
    y = list(acronym)
    for i in y:
        try:
            ch[i] = ch[i] + 1
        except KeyError:
            ch[i] = 1

    double = False

    for a in list(acronym):
        if ch[a] > 1:
            double = True

    return double
    # print acronym, double


def startchecker(acronym, tokens, code):
    # code 0 = normal, 1 = same, 2 = recurring
    tokenlen = len(tokens)
    ignore = ('and', 'of', 'the', 'on')
    start = []
    s = -1
    if code == 0: #recurring
        for i in range(0, tokenlen): #iteration thru the tokens
            if tokens[i].lower().startswith(acronym[0].lower()) and tokens[i] not in ignore: #checks if token is starting with the first letter of the acronym and not in ignore list
                s = i   #checks where the meaning checking should start
    else:
        for i in range(0, tokenlen): #iteration thru the tokens
            if tokens[i].lower().startswith(acronym[0].lower()) and tokens[i] not in ignore:
                start.append(i)   #appends all possible starts

        if code == 1: # same letter acronym
            if len(start) >= len(acronym): #if the number of possible starts is greater than or equal to the acronym length it's okay. unlike if lesser, the acronym meaning is probably not there
                s = start[len(start) - len(acronym)] #to get the possible start, get the difference between the acronym length and start length and set this as an index on the start array.
            else:
                s = -1
        elif code == 2: #recurring
            ch = {}
            y = list(acronym)
            for i in y:
                try:
                    ch[i] = ch[i] + 1
                except KeyError:
                    ch[i] = 1
            if len(start) > 0:
                try:
                    s = start[len(start) - ch[acronym[0]]] #set the starting index to the difference of the number of starts and the number of the first letter of the acronym
                except IndexError:
                    s = 0
    return s



def meaningchecker(tokens, acronym, *positional_parameters, **keyword_parameters): # meaningchecker(list, string)
# tokens - the words where to find the meaning of the acronym.
    start = -1  #initialize
    tokenlen = len(tokens)  #get the token length
    ignore = ('and', 'of', 'the', 'on')  # ignore list
    ignorecount = {}
    if ('start' in keyword_parameters):
        start = 0
    else:
        if checkifsameletter(acronym):
            start = startchecker(acronym, tokens, 1)
        elif checkifrecurringletter(acronym):
            start = startchecker(acronym, tokens, 2)
        else:
            start = startchecker(acronym, tokens, 0)
    accepted = False

    # print "meaningchecker", tokens, acronym

    if start != -1 and start+1 < tokenlen and len(acronym) > 1: #just checking if start != -1 w/c means the acronym may not be defined near it and if it's not a single letter only.
        a = 1 #init
        meaning = tokens[start] #meaning variable takes the value of the starting token.
        if meaning in ignore: #just checking if the first word is in ignore
            return (False, "")  #if yes, stop the process immediately.
        for j in range(start+1, tokenlen): #iteration thru the tokens

            # if tokens[j].lower().startswith(acronym[a].lower()): #if the words starts with the current letter of the acronym
            #     meaning = meaning + " " + tokens[j]  #add it
            #     print "1_added->", tokens[j]
            #     a = a + 1  #a is the counter and sentinel to check if the acronym meaning is completed.
            #     accepted = True # also keep tracks if whether the meaning is still accepted or not

            # print "checking.....", tokens[j]
            if tokens[j].lower().startswith(acronym[a].lower()): #if the words starts with the current letter of the acronymtok
                if not checkifrecurringletter(acronym):
                    if tokens[j] in ignore:
                        try:
                            if tokens[j+1].lower().startswith(acronym[a].lower()): #if yung next
                                # print "1_a", tokens[j]
                                meaning = meaning + " " + tokens[j] # added the ignore
                                accepted = True
                            else:
                                # print "1_b", tokens[j]
                                meaning = meaning + " " + tokens[j]  #add it
                                a = a + 1  #a is the counter and sentinel to check if the acronym meaning is completed.
                                accepted = True # also keep tracks if whether the meaning is still accepted or not
                        except IndexError:
                            # print "1_c", tokens[j]
                            meaning = meaning + " " + tokens[j]  #add it
                            a = a + 1  #a is the counter and sentinel to check if the acronym meaning is completed.
                            accepted = True # also keep tracks if whether the meaning is still accepted or no
                    else:
                        # print "1_d", tokens[j]
                        meaning = meaning + " " + tokens[j]  #add it
                        a = a + 1  #a is the counter and sentinel to check if the acronym meaning is completed.
                        accepted = True # also keep tracks if whether the meaning is still accepted or no
                else:
                    # print "1_e", tokens[j]
                    meaning = meaning + " " + tokens[j]  #add it
                    a = a + 1  #a is the counter and sentinel to check if the acronym meaning is completed.
                    accepted = True # also keep tracks if whether the meaning is still accepted or no

            elif tokens[j] in ignore: #if in ignore, it's fine. eg the words 'of', 'and' & 'the' are normally not included in the acronym but is included in the meaning.
                meaning = meaning + " " + tokens[j] #add it
                # print "2_added->", tokens[j]
                accepted = True #still accepted
                #this try and except statement keeps track if the ignored words appears only once. if not, the meaning is immediately unaccepted.
                try:
                    err = ignorecount[tokens[j]]
                    accepted = False
                    break
                except KeyError:
                    ignorecount[tokens[j]] = 1
            else:
                accepted = False
                break
            # print "accepted", accepted
            if len(acronym) == a: #checks if the acronym length is already achieved
                break

        if len(acronym) != a: #sometimes the looping process and the last checking of variable a and len(acronym) is not executed so it's a must to check if 'a' meets the length of the acronym
            accepted = False #if not, it's false. it's not the meaning of the acronym

        if accepted:
            # print acronym, meaning
            return (True, meaning)
        else:
            return (False, "")
    else:
        return (False, "")


def getacronym(tagged_sentences):
    acronyms = []
    for se in tagged_sentences:
        x = len(se)
        for i in range(0, x):
            if se[i][1] == "allCaps" or se[i][1] == "insideparen":
                acronyms.append(se[i][0])
    return list(set(acronyms))

def getacronymmeaning(acronyms, text):
    ls = []
    try:
        text = text.decode('utf-8')
        tokens = word_tokenize(text)
        x = len(tokens)
        for acronym in acronyms:
            for i in range(1, x):
                if tokens[i] == acronym:
                    # print "checking...", acronym
                    # print tokens[i], "--- ", i
                    init = 5
                    #there's a problem in here that sometimes when the range is not right, it returns an empty array.
                    # eg if an array has 5 elements and it was sliced from index 1 to 6, it will return an empty array
                    words = []
                    while not words:
                        s = i - len(acronym) - init
                        words = tokens[s:i]
                        init = init - 1
                    check, meaning = meaningchecker(words, acronym.replace('s', ''))
                    if check:
                        ls.append(meaning)
                        break
                    # else:
                        ls.append(acronym)
    except:
        ls = []
    return list(set(ls))


def matcher(tokens, acronym): # meaningchecker(list, string)
    # tokens - the words where to find the meaning of the acronym.
    start = 0  #initialize
    tokenlen = len(tokens)  #get the token length
    ignore = ('and', 'of', 'the', 'on')  # ignore list
    ignorecount = {}

    accepted = False

    if start != -1 and start+1 < tokenlen and len(acronym) > 1: #just checking if start != -1 w/c means the acronym may not be defined near it and if it's not a single letter only.
        a = 1 #init
        meaning = tokens[start] #meaning variable takes the value of the starting token.
        if meaning in ignore or not meaning.startswith(acronym[start].lower()): #just checking if meaning is in ignore
            return False  #if yes, stop the process immediately.
        for j in range(start+1, tokenlen): #iteration thru the tokens
            if tokens[j].lower().startswith(acronym[a].lower()): #if the words starts with the current letter of the acronym
                meaning = meaning + " " + tokens[j]  #add it
                a = a + 1  #a is the counter and sentinel to check if the acronym meaning is completed.
                accepted = True # also keep tracks if whether the meaning is still accepted or not
            elif tokens[j] in ignore: #if in ignore, it's fine. eg the words 'of', 'and' & 'the' are normally not included in the acronym but is included in the meaning.
                meaning = meaning + " " + tokens[j] #add it
                accepted = True #still accepted
                #this try and except statement keeps track if the ignored words appears only once. if not, the meaning is immediately unaccepted.
                try:
                    err = ignorecount[tokens[j]]
                    accepted = False
                    break
                except KeyError:
                    ignorecount[tokens[j]] = 1
            else:
                accepted = False
            if len(acronym) == a: #checks if the acronym length is already achieved
                break

        if len(acronym) != a: #sometimes the looping process and the last checking of variable a and len(acronym) is not executed so it's a must to check if 'a' meets the length of the acronym
            accepted = False #if not, it's false. it's not the meaning of the acronym

        if accepted:
            # print acronym, meaning
            return True
        else:
            return False
    else:
        return False

# print matcher(['Sugar', 'Regulatory', "Administrative"], 'SRA')