# coding=utf-8

import sys, re, string, warnings # built in python libraries

import site_packages.nltk as nltk # nltk
import site_packages.langdetect as langdetect # langdetect

from nltk.util import ngrams # from nltk

# custom libraries
# import data

warnings.filterwarnings('error', category = UnicodeWarning) #for warning conversion to error

data_shortcuts =[
    "jr",
    "mr",
    "mrs",
    "ms",
    "dr",
    "prof",
    "sr",
    "sen",
    "corp",
    "rep",
    "gov",
    "atty",
    "supt",
    "det",
    "rev",
    "col",
    "gen",
    "lt",
    "cmdr",
    "adm",
    "capt",
    "sgt",
    "cpl",
    "maj",
    "esq",
    "mstr",
    "phd",
    "adj",
    "adv",
    "asst",
    "bldg",
    "brig",
    "comdr",
    "hon",
    "messrs",
    "mlle",
    "mme",
    "op",
    "ord",
    "pvt",
    "reps",
    "res",
    "sens",
    "sfc",
    "surg",
    "pres",
    "sec",
    "supt",
    "pang",
    "engr",
    "dept",
    "mz",
    "mx",
    "br",
    "fr",
    "pr",
    "ave",
    "st",
    "brgy",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "jan",
    "feb",
    "mar",
    "apr",
    "jun",
    "jul",
    "aug",
    "sep",
    "sept",
    "oct",
    "nov",
    "dec",
    "comp", #computer
    "mt", #mountain
    "sta", #santa
    "ma" #maria
  ]
domains = [
    ".com",
    ".ph",
    ".net",
    ".jp",
    ".com.ph",
    ".net.ph",
    ".org",
    ".int",
    ".edu",
    ".edu.ph",
    ".gov",
    ".gov.ph",
    ".co",
    ".co.kr"
  ]
honorifics = [
    "Mr.",
    "Mrs.",
    "Ms.",
    "Sen.",
    "Dr.",
    "Prof.",
    "Usec",
    "Usec.",
    "Senator",
    "President",
    "Prime Minister",
    "Secretary",
    "Justice",
    "Mayor",
    "Pangulong",
    "Vice President",
    "Senadora"]
utf8seed = [
    ("ÃƒÂ±"     , "ñ"),
    ("Ãƒâ€˜"    , "Ñ" ),
    ("Ã¢â‚¬â„¢" , "\'"),
    ("ÃƒÂ¡"     , "á"),
    ("ÃƒÂ¤"     , "ä"),
    ("Ãƒâ€ž"    , "ä"),
    ("ÃƒÂ§"     , "ç"),
    ("ÃƒÂ©"     , "é"),
    ("Ãƒâ€°"    , "É"),
    ("ÃƒÂ¨"     , "è"),
    ("ÃƒÂ¬"     , "ě"),
    ("ÃƒÂª"     , "ê"),
    ("ÃƒÂ­"     , "í" ),
    ("ÃƒÂ¯"     , "ï"),
    ("Ã„Â©"     , "ĩ"),
    ("ÃƒÂ³"     , "ó"),
    ("ÃƒÂ¸"     , "ø"),
    ("ÃƒÂ¶"     , "ö"),
    ("Ãƒâ€“"    , "ö"),
    ("Ã…Â¡"     , "š"),
    ("ÃƒÂ¼"     , "ü"),
    ("LÃƒÂº"    , "ú"),
    ("Ã…Â©"     , "ũ"),
    ("Ã±"       , "ñ"),
    ("â‚¬"      , "€"),
    ("â€š"      , "‚"),
    ("Æ’"       , "ƒ"),
    ("â€ž"      , "„"),
    ("â€¦"      , "…"),
    ("â€"       , "†"),
    ("â€¡"      , "‡"),
    ("Ë†"       , "ˆ"),
    ("â€°"      , "‰"),
    ("Å"        , "Š"),
    ("â€¹"      , "‹"),
    ("Å’"       , "Œ"),
    ("Å½"       , "Ž"),
    ("â€˜"      , "\'"), #original : ‘
    ("â€™"      , "\'"), #original : ’
    ("â€œ"      , "\""), #orig : “
    ("â€"       , "\""), #orig : ”
    ("â€¢"      , "•"),
    ("â€“"      , "–"),
    ("â€”"      , "—"),
    ("Ëœ"       , "˜"),
    ("â„¢"      , "™"),
    ("Å¡"       , "š"),
    ("â€º"      , "›"),
    ("Å“"       , "œ"),
    ("Å¾"       , "ž"),
    ("Å¸"       , "Ÿ"),
    ("Â"        , " "),
    ("Â¡"       , "¡"),
    ("Â¢"       , "¢"),
    ("Â£"       , "£"),
    ("Â¤"       , "¤"),
    ("Â¥"       , "¥"),
    ("Â¦"       , "¦"),
    ("Â§"       , "§"),
    ("Â¨"       , "¨"),
    ("Â©"       , "©"),
    ("Âª"       , "ª"),
    ("Â«"       , "¬"),
    ("Â®"       , "®"),
    ("Â¯"       , "¯"),
    ("Â°"       , "°"),
    ("Â±"       , "±"),
    ("Â²"       , "²"),
    ("Â³"       , "³"),
    ("Â´"       , "\'"), #orig : ´
    ("Âµ"       , "µ"),
    ("Â¶"       , "¶"),
    ("Â·"       , "·"),
    ("Â¸"       , "¸"),
    ("Â¹"       , "¹"),
    ("Âº"       , "º"),
    ("Â»"       , "»"),
    ("Â¼"       , "¼"),
    ("Â½"       , "½"),
    ("Â¾"       , "¾"),
    ("Â¿"       , "¿"),
    ("Ã€"       , "À" ),
    ("Ã"        , "Á"  ),
    ("Ã‚"       , "Â" ),
    ("Ãƒ"       , "Ã" ),
    ("Ã„"       , "Ä" ),
    ("Ã…"       , "Å" ),
    ("Ã†"       , "Æ" ),
    ("Ã‡"       , "Ç" ),
    ("Ãˆ"       , "È" ),
    ("Ã‰"       , "É" ),
    ("ÃŠ"       , "Ê" ),
    ("Ã‹"       , "Ë" ),
    ("ÃŒ"       , "Ì" ),
    ("Ã"        , "Í"  ),
    ("ÃŽ"       , "Î" ),
    ("Ã"        , "Ï"  ),
    ("Ã"        , "Ð"  ),
    ("Á‘"       , "Ñ" ),
    ("Ã‘"       , "Ñ" ),
    ("Ã’"       , "Ò" ),
    ("Ã“"       , "Ó" ),
    ("Ã”"       , "Ô" ),
    ("Ã•"       , "Õ" ),
    ("Ã–"       , "Ö" ),
    ("Ã—"       , "×" ),
    ("Ã˜"       , "Ø" ),
    ("Ã™"       , "Ù" ),
    ("Ãš"       , "Ú" ),
    ("Ã›"       , "Û" ),
    ("Ãœ"       , "Ü" ),
    ("Ã"        , "Ý"  ),
    ("Ãž"       , "Þ" ),
    ("ÃŸ"       , "ß" ),
    ( "Ã"       , "à"  ),
    ("Ã¡"       , "á" ),
    ("Ã¢"       , "â" ),
    ("Ã£"       , "ã" ),
    ("Ã¤"       , "ä" ),
    ("Ã¥"       , "å" ),
    ("Ã¦"       , "æ" ),
    ("Ã§"       , "ç" ),
    ("Ã¨"       , "è" ),
    ("Ã©"       , "é" ),
    ("Ãª"       , "ê" ),
    ("Ã«"       , "ë" ),
    ("Ã¬"       , "ì" ),
    ( "Ã"       , "í" ),
    ("Ã®"       , "î" ),
    ("Ã¯"       , "ï" ),
    ("Ã°"       , "ð" ),
    ("Ã±"       , "ñ" ),
    ("Ã²"       , "ò" ),
    ("Ã³"       , "ó" ),
    ("Ã´"       , "ô" ),
    ("Ãµ"       , "õ" ),
    ("Ã¶"       , "ö" ),
    ("Ã·"       , "÷" ),
    ("Ã¸"       , "ø" ),
    ("Ã¹"       , "ù" ),
    ("Ãº"       , "ú" ),
    ("Ã»"       , "û" ),
    ("Ã¼"       , "ü" ),
    ("Ã½"       , "ý" ),
    ("Ã¾"       , "þ" ),
    ("Ã¿"       , "ÿ" ),
    ("“"        , "\""),
    ("”"        , "\""),
    ("‘"        , "\'"),
    ("’"        , "\'"),
    ("\n"       , " "),
    ("–"        , "-"),
    ("â€™"      , "\'"),
    ("†™"       , "\'"),
    ("``"       , "\""),
    ("`"        , "\'"),];
trashparts = [
    'DISCLAIMER: Sun.Star website welcomes friendly debate, but comments posted on this site do not necessary reflect the views of the Sun.Star management and its affiliates. Sun.Star reserves the right to delete, reproduce or modify comments posted here without notice. Posts that are inappropriate will automatically be deleted. Forum rules: Do not use obscenity. Some words have been banned. Stick to the topic. Do not veer away from the discussion. Be coherent and respectful. Do not shout or use CAPITAL LETTERS!  Please enable JavaScript to view the comments powered by Disqus.',
    'Share this:Share on Facebook (Opens in new window)Click to share on Twitter (Opens in new window)Click to share on Google+ (Opens in new window)Click to share on Tumblr (Opens in new window)Click to share on Reddit (Opens in new window)Click to email this to a friend (Opens in new window)Click to print (Opens in new window)MoreClick to share on Pinterest (Opens in new window)Click to share on LinkedIn (Opens in new window)  Related  comments',
    'InterAksyon.com The online news portal of TV5 MANILA',
    'Business ( Article MRec ), pagematch: 1, sectionmatch: 1',
    'Headlines ( Article MRec ), pagematch: 1, sectionmatch: 1',
    'Article MRec',
    'pagematch: 1, sectionmatch: 1'
    ]
contraction_shortcuts = {
    "Jan.": "January",
    "Feb.": "February",
    "Mar.": "March",
    "Apr.": "April",
    "Jun.": "June",
    "Jul.": "July",
    "Aug.": "August",
    "Sep.": "September",
    "Sept.": "September",
    "Oct.": "October",
    "Nov.": "November",
    "Dec.": "December",
    "Mon.": "Monday",
    "Tue.": "Tuesday",
    "Wed.": "Wednesday",
    "Thu.": "Thursday",
    "Fri.": "Friday",

    "ain't": "am not", #are not; is not; has not; have not
    "aren't": "are not", #am not
    "can't": "cannot",
    "can't've": "cannot have",
    "'cause": "because",
    "could've": "could have",
    "couldn't": "could not",
    "couldn't've": "could not have",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "hadn't": "had not",
    "hadn't've": "had not have",
    "hasn't": "has not",
    "haven't": "have not",
    "he'd": "he had", #he would
    "he'd've": "he would have",
    "he'll": "he shall", #he will
    "he'll've": "he shall have", #he will have
    "he's": "he has", #he is
    "how'd": "how did",
    "how'd'y": "how do you",
    "how'll": "how will",
    "how's": "how has", #how is | how does
    "I'd": "I had", #I would
    "I'd've": "I would have",
    "I'll": "I shall", #I will
    "I'll've": "I shall have", #I will have
    "I'm": "I am",
    "I've": "I have",
    "isn't": "is not",
    "it'd": "it had", #it would
    "it'd've": "it would have",
    "it'll": "it shall", #it will
    "it'll've": "it shall have", #it will have
    "it's": "it has", #it is
    "let's": "let us",
    "ma'am": "madam",
    "mayn't": "may not",
    "might've": "might have",
    "mightn't": "might not",
    "mightn't've": "might not have",
    "must've": "must have",
    "mustn't": "must not",
    "mustn't've": "must not have",
    "needn't": "need not",
    "needn't've": "need not have",
    "o'clock": "of the clock",
    "oughtn't": "ought not",
    "oughtn't've": "ought not have",
    "shan't": "shall not",
    "sha'n't": "shall not",
    "shan't've": "shall not have",
    "she'd": "she had", #she would
    "she'd've": "she would have",
    "she'll": "she shall", #she will
    "she'll've": "she shall have", #she will have
    "she's": "she has", #she is
    "should've": "should have",
    "shouldn't": "should not",
    "shouldn't've": "should not have",
    "so've": "so have",
    "so's": "so as", #so is
    "that'd": "that would", #that had
    "that'd've": "that would have",
    "that's": "that has", #that is
    "there'd": "there had", #there would
    "there'd've": "there would have",
    "there's": "there has", #there is
    "they'd": "they had", #they would
    "they'd've": "they would have",
    "they'll": "they shall", #they will
    "they'll've": "they shall have", #they will have
    "they're": "they are",
    "they've": "they have",
    "to've": "to have",
    "wasn't": "was not",
    "we'd": "we had", #we would
    "we'd've": "we would have",
    "we'll": "we will",
    "we'll've": "we will have",
    "we're": "we are",
    "we've": "we have",
    "weren't": "were not",
    "what'll": "what shall", #what will
    "what'll've": "what shall have", #what will have
    "what're": "what are",
    "what's": "what has", #what is
    "what've": "what have",
    "when's": "when has", #when is
    "when've": "when have",
    "where'd": "where did",
    "where's": "where has", #where is
    "where've": "where have",
    "who'll": "who shall", #who will
    "who'll've": "who shall have", #who will have
    "who's": "who has", #who is
    "who've": "who have",
    "why's": "why has", #why is
    "why've": "why have",
    "will've": "will have",
    "won't": "will not",
    "won't've": "will not have",
    "would've": "would have",
    "wouldn't": "would not",
    "wouldn't've": "would not have",
    "y'all": "you all",
    "y'all'd": "you all would",
    "y'all'd've": "you all would have",
    "y'all're": "you all are",
    "y'all've": "you all have",
    "you'd": "you had", #you would
    "you'd've": "you would have",
    "you'll": "you shall", #you will
    "you'll've": "you shall have", #you will have
    "you're": "you are",
    "you've": "you have",
    "gov't" : "government",
    "Pres." : "President"
 }
languages = {
    "af" : "Afrikaans",
    "ar" : "Arabic",
    "bg" : "Bulgarian",
    "bn" : "Bengali",
    "cs" : "Czech",
    "da" : "Danish",
    "de" : "German",
    "el" : "Greek",
    "en" : "English",
    "es" : "Spanish",
    "fa" : "Persian",
    "fi" : "Finnish",
    "fr" : "French",
    "gu" : "Gujarati",
    "he" : "Hebrew",
    "hi" : "Hindi",
    "hr" : "Croatian",
    "hu" : "Hungarian",
    "id" : "Indonesian",
    "ja" : "Japanese",
    "kn" : "Kannada",
    "ko" : "Korean",
    "lt" : "Lithuanian",
    "lv" : "Latvian",
    "ml" : "Malayalam",
    "mr" : "Marathi",
    "ne" : "Nepali",
    "nl" : "Dutch",
    "no" : "Norwegian",
    "pa" : "Punjabi",
    "pl" : "Polish",
    "pt" : "Portuguese",
    "ro" : "Romanian",
    "ru" : "Russian",
    "sk" : "Slovak",
    "sl" : "Slovene",
    "so" : "Somali",
    "sq" : "Albanian",
    "sv" : "Swedish",
    "sw" : "Swahili",
    "ta" : "Tamil",
    "te" : "Telugu",
    "th" : "Thai",
    "tl" : "Tagalog",
    "tr" : "Turkish",
    "uk" : "Ukrainian",
    "ur" : "Urdu",
    "vi" : "Vietnamese",
    "zh-cn" : " Simplified Chinese",
    "zh-tw" : " Traditional Chinese"
    }

# checks if the given token is not a numeric entity like float, integer or whatsoever. used in sentence segmentation. I/O: string (token) / boolean (True - if numeric | False - numeric)
def is_not_numeric(token):
    try:
        float(token)
        return False
    except ValueError:
        return True

##### finder

# checks if the given token is a number. can also be used in money entities like "P48 Billion"  similar to is_not_numeric but the result is different. if token is a number, then the result is true, else, false. used in get_num() and determine_duplicates() I/O : string (token) / boolean (True - if number | False - if not number)
def checkifnum(token):
    repl = ['-',  'P', ',']
    for r in repl:
        token = token.replace(r, '').strip()
    try:
        float(token)
        return True
    except ValueError:
        return False

# gets the last word in a sentence. similar to getLastWord but has different result. it returns the last word and the starting index of the last word minus one. used in get_num() function I/O : string (token) / tuple (string, int) -> (lastWord, starting_index_minus_one)
def get_last(token):
    words = token.split()
    try:
        lastWord = words[len(words)-1]
        return (lastWord, len(token)-len(lastWord)-1)
    except IndexError:
        return (token, -1)

# checks if the token is a valid year. so far years from 1100 to 3000 are allowed. used in getYear(). I/O : string (token) / tuple (boolean, int - True | string - False) the second element is the token.
def is_year(token):
    token = re.sub('[^0-9a-zA-Z]+', ' ', token)
    try:
        z = int(token)
        if z < 3000 and z > 1100:
            return (True, z)
        else:
            return (False, token)
    except ValueError:
        return (False, token)

# gets the list of years present in a text. uses is_year() to check if a token inside the text is a valid year. used in find_date(). I/O: string (text) / list (string - list of years)
def getYear(text):
    words = text.split(' ')
    years = []
    for w in words:
        ans = is_year(w)
        if ans[0]:
            years.append(str(ans[1]))
    return list(set(years))

# segregate is a helper function which separates one word and non single (multiple word) entities. used in check_date_duplicates(). I/O : list (entities - array of words, or in use, this should be an array of dates) /  tuple (list, list) - (array of single words, array of non single words)
def segregate(entities):
    single = []
    non_single = []
    for entity in entities:
        if len(entity.split()) == 1:
            single.append(entity) #single are either month or year
        else:
            non_single.append(entity)
    return (single, non_single)

# check_date_duplicates is a function that check if there are date duplicates. used in find_date(). eg. "May" and "May 2016". "May" should be removed since it was considered as a duplicate of "May 2016". I/O : two params (list, list) - (dates, years) / list (list of no duplicate dates)
def check_date_duplicates(dates, years):
    no_duplicate_dates = []
    found = False
    for year in years:
        for date in dates:
            if year == date:
                found = True
                dates.remove(date)
        if found:
            years.remove(year)
    no_duplicate_dates.extend(years)
    no_duplicate_dates.extend(dates)

    singles, non_single = segregate(no_duplicate_dates)
    for single in singles:
        for ns in non_single:
            if single in ns:
                no_duplicate_dates.remove(single)
    return no_duplicate_dates

# find_date is a function that gets all the valid dates in the given text. wasn't used in any function so far. I/O: string (text) / list (string - list of dates)
def find_date(text):
    dates = []
    months = [("January", 31), ("February", 29), ("March", 31),  ("April", 30), ("May", 31), ("June", 30), ("July",31), ("August", 31), ("September", 30), ("October", 31), ("November",30), ("December", 31)]
    for m in months:
        found = True
        while found:
            idx = text.find(m[0])
            if idx != -1 and text[idx+len(m[0])] == " ": # added checker if next character of the month detected is a space, therefore it's a sole word and not inside a word.
                date = get_next_word(text[idx+len(m[0]):len(text)])
                posYear = get_next_word(text[idx+len(m[0])+len(date)+1: len(text)])

                date = date.replace(',', '')
                date = date.replace('.', '')

                try:
                    if int(date) <= m[1]:
                        z = is_year(posYear)
                        if z[0]:
                            dates.append(m[0]+" "+date+", "+str(z[1])) #full date like December 7, 2015
                        else:
                            dates.append(m[0]+" "+date) #date with no year like December 7
                    else:
                        z = is_year(date)
                        if z[0]:
                            dates.append(m[0]+" "+str(z[1])) #date with month and year only like December 2015
                except ValueError:
                    dates.append(m[0]) #Month only
            else:
                found = False
            text = text[idx+len(m[0]):len(text)]
    dates = check_date_duplicates(dates, getYear(text))
    return list(set(dates))

# get_num is a function that gets all large number entities given the large number name within a given text. for example, "billion" was given as the 2nd parameter, all number entities ending with billion would be extracted like 4 billion, 5 billion, etc. used in getmoney(). I/O : two params (string, string) - (raw text, large number name) / list (string - list of large number entities)
def get_num(text, large_number_name):
    results = []
    x = 0
    while x != -1:
        text = text[x+len(large_number_name):len(text)]
        x = text.find(large_number_name)
        potential = get_last(text[0:x])
        if checkifnum(potential[0]):
            results.append(text[potential[1]:x+len(large_number_name)].strip())
    return results

# getmoney is a function that gets all large number quantities in a given text. it uses get_num(). wasn't used in metawhale_topics.py at the moment. I/O : string (text) / list (string - list of large number entities)
def getmoney(text):
    money = []
    money.extend(get_num(text,'billion'))
    money.extend(get_num(text, 'percent'))
    money.extend(get_num(text, 'million'))
    money.extend(get_num(text, 'trillion'))
    money.extend(get_num(text, 'hectares'))
    return money

# [in main] getsocialtokens is a function that gets all social tokens (hashtag & username) in a given text. I/O : string (text) / list (string - list of social tokens)
def getsocialtokens(text):
    tokens = text.split()
    socialterms = []
    for token in tokens:
        token = re.sub('[^0-9a-zA-Z@#]+', '', token)
        if token.startswith(('#', '@')):
            if is_not_numeric(token[1:len(token)]):
                alphanumeric = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y','z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
                while not token.endswith(alphanumeric):
                    token = token[0:len(token)-1]
                socialterms.append(token)
    return list(set(socialterms))

# [in main] getacronyms is a function that calls acronymfinder.getacronymmeaning() and returns the entities with acronym in a text. for example in this sentence: "I am from the Polytechnic University of the Philippines (PUP)." the function detects "PUP" as an acronym and getacronymmeaning() function would find the meaning of this acronym througout the text. getacronyms would return the list of entities from getacronymmeaning(). I/O: two params (list, string) - (string - list of acronyms, raw text) / list (string - list of acronym entities)
def getacronyms(acronyms, text):
    try:
        acro = getacronymmeaning(acronyms, text)
    except (UnicodeDecodeError, UnicodeEncodeError):
        acro = []
    except:
        # acro = ['SomeError', sys.exc_info()[0]]
        acro = []

    return acro



# finding a one-word term in a string. I: two params (word to find, text)
# if word is a single string, it would find the word and return True or False
# if word is a tuple, it would return True if a value in the tuple is found
def find_word(string, word):
    tokens = string.split()
    value = (False, None)
    if type(word) == str:
        if word in tokens:
            value = (True, None)
    elif type(word) == tuple:
        for w in word:
            if w in tokens:
                value = (True, w)
                break
    return value

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


#removal of nuisance topic pattern: 2016 + nuisance word (eg: 2016 Wondering) normally, this topic would get 1 frequency towards the whole article and is not relevant at all.
def remove_unnecessary_year_word_combination(topic_freq_count):
    to_be_removed = []
    for topic in topic_freq_count:
        try:
            tokens = topic[0].split()
            res, year = is_year(tokens[0]) #for topics starting with a year
            if res and topic[1] <= 1:
                to_be_removed.append(topic)
        except IndexError: #just in case, but this shouldn't happen since topic_freq_count has a format of list of tuples
            pass

    for tbr in to_be_removed:
        topic_freq_count.remove(tbr)
    return topic_freq_count