from nltk.tokenize import word_tokenize
import data
import pos_tagger



shortcuts = data.shortcuts
domains = data.domains

def getLastword(chunk):
    words = chunk.split()
    lastWord = words[len(words)-1]
    lastWord = lastWord.replace('.', '').strip()
    return lastWord

def getNextWord(chunk):
    try:
        if chunk != "" or chunk !='':
            words = chunk.split()
            return words[0]
        else:
            return chunk
    except IndexError:
        return chunk

def checkIfNotDomain(text):
    if text in domains:
        return False
    else:
        return True

def checkIfNotShortcut(text):
    if text.lower() in shortcuts:
        return False
    else:
        return True

def isNotNumeric(s):
    try:
        float(s)
        return False
    except ValueError:
        return True

def sentencesplitter(chunk):
    charArray = list(chunk)
    sentences = []
    sentence = ""
    i = 0
    for c in charArray:
        sentence = sentence + c
        if c == '.':
            lastWord = getLastword(sentence)
            nextWord = getNextWord(chunk[i:len(chunk)])
            if checkIfNotShortcut(lastWord) and isNotNumeric(nextWord) and checkIfNotDomain(nextWord):
                sentences.append(sentence[:-1].strip())
                sentence = ""
        elif c == '?':
            sentences.append(sentence[:-1].strip())
            sentence = ""
        elif c == '!':
            sentences.append(sentence[:-1].strip())
            sentence = ""
        elif c == ';':
            sentences.append(sentence[:-1].strip())
            sentence = ""
        # elif c == ',':
        #     nextWord = getNextWord(chunk[i+1:len(chunk)])
        #     if isNotNumeric(nextWord):
        #         sentences.append(sentence[:-1].strip())
        #         sentence = ""
        elif i == len(chunk)-1:
            sentences.append(sentence.strip())
            sentence = ""
        i = i+1
    return sentences

def checkifnum(chunk):
    repl = ['-',  'P', ',']
    for r in repl:
        chunk = chunk.replace(r, '').strip()
    try:
        float(chunk)
        return True
    except ValueError:
        return False


def getpos(sentences):
    days = ('Sunday', "Monday", 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
    name_shortcuts_mid = ('de', 'del', 'dela', 'los') # name connectors that are usually in the middles
    name_shortcuts_period = ('Ma', 'Sta') #name shortcuts that are usually followed by period
    tg_adj = ('gaya')
    tg_adv = ('rin', 'din')
    tg_pronoun = ('siya','saan', 'ano', 'sino', 'kailan')
    tg_preposition = ('sa', 'ng', 'para')
    tg_determiner = ('ang', 'mga', 'ito')
    tg_conjunction = ('ngunit', 'pero')
    tg_cd = ('isa', 'isang', 'dalawa', 'dalawang')
    en_adv = ('between', 'around', 'behind', 'down')
    # posClass = pos_tagger.PosTaggerClass()
    tagged_text = []
    # orig_tag = []
    for sentence in sentences:
        sent = []
        # sentence = posClass.wordTagging(sentence)
        # orig_tag.append(sentence)
        for i in range(0, len(sentence)):
            tag = ""
            if sentence[i][0] in days:
                tag = "daysOfTheWeek"
            elif sentence[i][0] in months:
                tag = "dateMonth"
            elif sentence[i][0] in name_shortcuts_mid:
                tag = "ns_mid"
            elif sentence[i][0] in name_shortcuts_period:
                tag = "ns_period"
            elif sentence[i][0] in tg_adj:
                tag = "JJ"
            elif sentence[i][0] in tg_adv:
                tag = "RB"
            elif sentence[i][0].lower() in tg_pronoun:
                tag = "PRP"
            elif sentence[i][0].lower() in tg_preposition:
                if sentence[i][0].istitle():
                    try:
                        if not sentence[i-1][0].istitle():
                            tag = "IN"
                    except IndexError:
                        pass
                else:
                    tag = "IN"
            elif sentence[i][0].lower() in tg_determiner:
                if sentence[i][0].istitle():
                    try:
                        if not sentence[i-1][0].istitle():
                            tag = "DT"
                    except IndexError:
                        pass
                else:
                    tag = "DT"
            elif sentence[i][0].lower() in tg_conjunction:
                if sentence[i][0].istitle():
                    try:
                        if not sentence[i-1][0].istitle():
                            tag = "CC"
                    except IndexError:
                        pass
                else:
                    tag = "CC"
            elif sentence[i][0].lower() in tg_cd:
                tag = "CD"
            elif sentence[i][0].lower() in en_adv:
                if sentence[i][0].istitle():
                    try:
                        # if the word before the adverb is not "the"
                        if not sentence[i-1][0] == "the":
                            tag = "RB"
                    except IndexError:
                        tag = "RB"
                else:
                    tag = "RB"

            if sentence[i][0].isupper():
                if sentence[i][0].endswith('.'):
                    tag = "capPeriod"
                elif checkifnum(sentence[i][0]):
                    tag = "CD"
                else:
                    tag = "allCaps"

            if sentence[i][0][len(sentence[i][0])-1] == "s":
                if sentence[i][0][0:len(sentence[i][0])-1].isupper():
                    tag = "allCaps"

            if sentence[i][0] == "-":
                tag = "-"
            elif sentence[i][0] == ",":
                tag = ","
            elif sentence[i][0] == "(":
                tag = ")"
            elif sentence[i][0] == ")":
                tag = ")"
            elif sentence[i][0] == ".":
                tag = "."
            elif sentence[i][0] == "@":
                tag = "@"

            if i == len(sentence)-1:
                tag = "_end"

            try:
                if sentence[i-1][0] == "(" and sentence[i+1][0] == ")" and len(sentence[i][0]) > 1:
                    tag = "insideparen"
            except IndexError:
                pass

            if tag:
                sent.append([sentence[i][0], tag])
            else:
                sent.append([sentence[i][0], sentence[i][1]])
        tagged_text.append(sent)
    return tagged_text

def checkerpos(tagged_sentences):
    #context free grammar like checking
    #where the decision trees are located

    accepted_topics = [] #initialization
    for se in tagged_sentences: #looping per sentence
        x = len(se) #gets the length
        for i in range(0, x): #looping per word in the sentence
            w1 = se[i] #assignment
            # if w1[1] == "CD": # for qty
            #     #variable 'nn' is the topic
            #     if i>0:
            #         if not se[i-1][1] == "dateMonth":
            #             nn = w1[0] #start
            #             while i+1 < x: #checks if the next word is not the end of the sentence (important to avoid errors)
            #                 if se[i+1][1] == 'NN' or se[i+1][1] == "NNS" : #if it's classified as normal, then ok
            #                     i = i + 1 #increment
            #                     se[i][1] = "nn_digit"
            #                     nn = nn +" "+ se[i][0] # appends to nn
            #                 elif se[i+1][1] == "CD": # if it's a quantity, then also ok
            #                     if not se[i][1] == "nn_digit":
            #                         i = i + 1
            #                         se[i][1] = "--"
            #                         nn = nn +" "+ se[i][0]
            #                         break #but the process would stop after
            #                     else:
            #                         break
            #                 else:
            #                     break
            #     if not nn == w1[0]: #if nn is not the same as before, then it's accepted
            #         # print nn, "_qty"
            #         nn = nn+"_digit"
            #         accepted_topics.append(nn)

            # if w1[1] == "NNP":
            #     nn = w1[0]
            #     while i+1 < x:
            #         if se[i+1][1] == "NNP" or se[i+1][1] == "NNPS" or se[i+1][1] == "ns_mid":
            #             i = i + 1
            #             se[i][1] = "--"
            #             nn = nn + " " + se[i][0]
            #         elif se[i+1][1] == "ns_period":
            #             try:
            #                 if se[i+2][1] == ".":
            #                     i = i + 1
            #                     se[i][1] = "--"
            #                     nn = nn + " " + se[i][0] #ns_period
            #                     i = i + 1
            #                     se[i][1] = "--"
            #                     nn = nn + se[i][0] #period
            #                 else:
            #                     i = i + 1
            #             except IndexError:
            #                 i = i + 1
            #         else:
            #             break
            #     nn = nn + "_pn"
            #     accepted_topics.append(nn)

            if w1[1] == "NN":
                nn = w1[0]
                while i+1 < x:
                    if se[i+1][1] == "NN" or se[i+1][1] == "NNS" or se[i+1][1] == "JJ":
                        i = i + 1
                        se[i][1] = "--"
                        nn = nn + " " + se[i][0]
                    else:
                        break
                if not nn == w1[0]:
                    nn = nn + "_nn"
                    accepted_topics.append(nn)

            elif w1[1] == "allCaps":
                # print w1[0], "_acronym"
                nn = w1[0] + "_acronym"
                accepted_topics.append(nn)

    return list(set(accepted_topics))

