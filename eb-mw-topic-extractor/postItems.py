#!/usr/bin/python
# -*- coding: utf-8 -*- 

sentenceWordsArray = [] 
sentencePOS_Array = []
starter = ["DT","IN","JJ","CC","SYMBOL","VBG","NN"]
stoppers = [
    'EX',
    'LS',
    'MD',
    'PDT',
    'POS',
    'PRP',
    'PRP$',
    'RB',
    'RBR',
    'RBS',
    'RP',
    'SYM',
    'TO',
    'UH',
    'VB',
    'VBD',
    'VBG',
    'VBN',
    'VBP',
    'VBZ',
    'WDT',
    'WP',
    'WP$',
    'WRB',
    "SYMBOL"
]

spanish_connector = ["del","de","dela","delas","delos","los"]
spanish_connector_two = ['la',"los","las","al"]

conjuctionsintitles = [
    'on',
    'of',
    'and',
    'to'
]
notallowed = ["Inc.","and"]
posIndexer = [
    "NNP",
    "NNPS",
    "NN",
    "NNS",
    "CC",
    "JJ",
    "IN",
    "NNP-NNP",
    "NNP-NNS",
    "POS",
    "FW",
    "DT",
    "CD"
]

posIndexerNouns =  [
    "NNP",
    "NNPS",
    "NN",
    "NNS", 
    "NNP-NNP",
    "NNP-NNS", 
]

name_suffixes = [
    "B.V.M.", 
    "CFRE", 
    "CLU", 
    "CPA", 
    "C.S.C.", 
    "C.S.J.", 
    "D.C.", 
    "D.D.", 
    "D.D.S.", 
    "D.M.D.", 
    "D.O.", 
    "D.V.M.", 
    "Ed.D.", 
    "Esq.", 
    "II", 
    "III", 
    "IV", 
    "Inc.", 
    "J.D.", 
    "Jr.", 
    "LL.D.", 
    "Ltd.", 
    "M.D.", 
    "O.D.", 
    "O.S.B.", 
    "P.C.", 
    "P.E.", 
    "PhD.", 
    "Ph.D.", 
    "Ret.", 
    "R.G.S", 
    "R.N.", 
    "R.N.C.", 
    "S.H.C.J.", 
    "S.J.", 
    "S.N.J.M.", 
    "Sr.", 
    "S.S.M.O.", 
    "MA.", 
    "MBA.", 
    "MS.", 
    "MSW.",
    "Rep.",
    'Sen.',
    "Gov.",
    "Pres.",
    "Atty."
]

qoutationSymbols = [
    "'",
    '"',
    "``",
    "“",
    "”",
    "‘",
    "’",
    "''"
]


paraList = []
posDictionary = {
    'CC':'Coordinating conjunction',
    'CD':'Cardinal number',
    'DT':'Determiner',
    'EX':'Existential there',
    'FW':'Foreign word',
    'IN':'Preposition or subordinating conjunction',
    'JJ':'Adjective',
    'JJR':'Adjective - comparative',
    'JJS':'Adjective - superlative',
    'LS':'List item marker',
    'MD':'Modal',
    'NN':'Noun - singular or mass',
    'NNS':'Noun - plural',
    'NNP':'Proper noun - singular',
    'NNPS':'Proper noun - plural',
    'PDT':'Predeterminer',
    'POS':'Possessive ending',
    'PRP':'Personal pronoun',
    'PRP$':'Possessive pronoun',
    'RB':'Adverb',
    'RBR':'Adverb - comparative',
    'RBS':'Adverb - superlative',
    'RP':'Particle',
    'SYM':'Symbol',
    'TO':'to',
    'UH':'Interjection',
    'VB':'Verb - base form',
    'VBD':'Verb - past tense',
    'VBG':'Verb - gerund or present participle',
    'VBN':'Verb - past participle',
    'VBP':'Verb - non-3rd person singular present',
    'VBZ':'Verb - 3rd person singular present',
    'WDT':'Wh-determiner',
    'WP':'Wh-pronoun',
    'WP$':'Possessive wh-pronoun',
    'WRB':'Wh-adverb'
}

posEnglishFix = {
    "N" : "NN",
    "STOPPER" : "SYMBOL",
    "CONJ" : "CC",
    "ADV" : "RB",
    "PREP" : "IN",
    "DT" : "DT",
    "VBL" : "VB",
    "V" : "VB",
    "UNK" : "UNK",
    "PR": "PRP",
    "ADJ": "JJ",
    "PRON": "PRP"
}

pos_dictionary = {
    "nn":"noun",
    "adj":"adjective",
    "adv":"adverb",
    "pro":"pronoun",
    "pre":"preposition",
    "int":"interjection",
    "ver":"verb",
    "con":"conjunction"
}

tagalogApos = {
    "y":"ay",
    "t":"at"
}

englishPronouns = [
    "I", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
    "I", "you", "he", "she", "it", "we", "they", "what", "who",
    "me", "him", "her", "it", "us", "you", "them", "whom",
    "mine", "yours", "his", "hers", "ours", "theirs",
    "this", "that", "these", "those",
    "who", "whom", "which", "what", "whose", "whoever", "whatever", "whichever", "whomever",
    "who", "whom", "whose", "which", "that", "what", "whatever", "whoever", "whomever", "whichever",
    "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
    "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves",
    "Each other", "one another",
    "Anything", "everybody", "another", "each", "few", "many", "none", "some", "all", "any", "anybody", "anyone", "everyone", "everything", "no one", "nobody", "nothing", "none", "other", "others", "several", "somebody", "someone", "something", "most", "enough", "little", "more", "both", "either", "neither", "one", "much", "such",
]

removeDaysoftheWeek = [
    "kahapon",
    "yesterday",
    "ngayon",
    "today",
    "bukas",
    "tomorrow",
    "lunes",
    "monday",
    "martes",
    "tuesday",
    "miyerkules",
    "wednesday",
    "huwebes", 
    "thursday",
    "biyernes", 
    "friday",
    "sabado", 
    "saturday",
    "linggo", 
    "sunday",
    "umaga",
    "hapon",
    "tanghali",
    "gabi"
]

# def changetoarray():
#     dict_target = open('custom_dictionary/englishwords.py', 'w')
#     enword_list = [word.replace('\n','') for word in open("custom_dictionary/words.txt","r").readlines()]

#     dict_target.write('words = [')
#     dict_target.write("\n")

#     for word in enword_list: 
#         oldword = '    "__xxx__",'

#         word = word.replace('"','\\"')
#         word = word.replace("'","\\'")

#         word = oldword.replace("__xxx__",word)
#         dict_target.write(word)
#         dict_target.write("\n")

#     dict_target.write(']')
#     dict_target.write("\n")

#     dict_target.close()

# changetoarray()