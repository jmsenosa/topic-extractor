import data
from metawhale_topics_functions import is_not_numeric as is_not_numeric

data_shortcuts = data.shortcuts
domains        = data.domains
honorifics     = data.honorifics

# get the last word in the given string. used in sentence segmentation I/O: string (sentence) / string (lastWord)
def get_last_word(sentence):
    words = sentence.split()
    lastWord = words[len(words)-1]
    lastWord = lastWord.replace('.', '').strip()
    return lastWord

# gets the first word in the given string. used in sentence segmentation I/O : string (sentence) / string (first word)
def get_next_word(sentence):
    try:
        if sentence != "" or sentence !='':
            words = sentence.split()
            return words[0]
        else:
            return sentence
    except IndexError:
        return sentence

# checks if the given token is not a domain. see data.domains to check the domains list. used in sentence segmentation. I/O: string (token) / boolean (True | False)
def check_if_not_domain(token):
    if token in domains:
        return False
    else:
        return True

# checks if the given token is not a shortcut. see data.shortcuts to check the list of shortcuts. used in sentence segmentation. I/O: string (token) / boolean (True | False)
def check_if_not_shortcut(token):
    token = token.lower()
    if token in data_shortcuts:
        return False
    else:
        return True

# [in main] the whole sentence segmentation algorithm. I/O : string (raw text) / list (fin - list of sentences in that raw text)
def sentence_splitter(text):
    charArray = list(text) #converting to whole text into an array of characters
    sentences = [] # init for the batch sentences
    sentence = "" # init for each sentence
    i = 0 # init
    for c in charArray: # looping thru the array of characters
        sentence = sentence + c # adding the current letter to the current sentence
        if c == '.': # if the current character is a period, several checking would happen to determine if it's really the end of the sentence.
            lastWord = get_last_word(sentence)
            nextWord = get_next_word(text[i:len(text)])
            ans = check_if_not_shortcut(lastWord)
            if check_if_not_shortcut(lastWord) and is_not_numeric(nextWord) and check_if_not_domain(nextWord):
                sentences.append(sentence.strip())
                sentence = ""
        elif c == '?': # question mark separator
            sentences.append(sentence.strip())
            sentence = ""
        elif c == '!': # exclamation point separator
            sentences.append(sentence.strip())
            sentence = ""
        elif c == ';': # semi-colon separator
            sentences.append(sentence.strip())
            sentence = ""
        elif i == len(text)-1: # if counter is already the length of the text, but it seems like it wasn't a sentence ender. the text could be ended without a proper punctuation mark. if this happens, end the process then append the current sentence.
            sentences.append(sentence.strip())
            sentence = ""
        i = i+1 # counter up

    fin = [] # init
    for sen in sentences: # looping thru
        if sen: # if sentence is not empty
            fin.append(sen) # append to final batch of sentences

    return fin
