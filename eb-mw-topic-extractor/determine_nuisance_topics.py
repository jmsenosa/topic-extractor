# coding=utf-8
import string

# nuisance topic functions
# Checks if the topic is composed of words that starts with different case.
# Used for checking nuisance topics that starts with a small letter but has a different case afterwards.
# Eg.: "sa mga LGBT" (e769cddc6d5f1bf1e6ee19e84e5f6c9e) - nuisance topic because it has no sense and not a stand alone topic.
# Another example is "ng Kristiyano" (e769cddc6d5f1bf1e6ee19e84e5f6c9e)
# "sa mga LGBT" = True | "daang matuwid" = False | "Manny Pacquiao" = False
# I/O: string / boolean
def check_if_irregular_case(topic):

    tokens = topic.split()
    check = False

    if topic[0].islower(): #first letter is lowercase
        for token in tokens:
            if token[0].isupper():
                check = True
                break
    else:
        for token in tokens:
            if token[0].islower():
                check = True
                break
    return check

# [in main] nuisance_removal is a function that removes unnecessary topics or what we call nuisance topics. these are normally prepositions, verbs, conjunctions, adjectives and adverbs that were wrongly extracted by the topic extraction algorithm which normally occurs in Taglish articles.
# I/O : two params (list, dictionary) - (array of topics , nuisance dictionary)
def nuisance_removal(topics, nuisance_dict):
    nuisance = [] #init
    check_dictionary = False

    if nuisance_dict:
        check_dictionary = True

    for topic in topics:
        if topic[0].islower() and check_if_irregular_case(topic):
            nuisance.append(topic)

        if check_dictionary and len(topic.split()) == 1:
            try:
                if nuisance_dict[topic.lower()]:
                    nuisance.append(topic)
            except KeyError:
                pass
    for n in nuisance:
        topics.remove(n)

    fin_topics = []
    for topic in topics:
        tokens = topic.split()
        flag = False
        cropped = ""
        for token in tokens:

            try:
                if nuisance_dict[token.lower()] == "NN" :
                    flag = True
                else:
                    if not flag: #just to make sure that it's still false, thus, if the flag became True, there's no way it will be False again. Fix to prevent the removal of nuisance words inside a valid topic
                        flag = False
            except KeyError:
                flag = True
            if flag:
                cropped = cropped +token + " "
        try:
            float(cropped.replace(' ', ''))
        except ValueError:
            if cropped: # to check if it's not blank
                fin_topics.append(cropped)
            # fin_topics.append(temp_topic)

        # for topic in fin_topics:
    return fin_topics

# [in main] remove_non_enders is a function that removes unnecessary last words on topics. these are normally prepositions, verbs, conjunctions, adjectives and adverbs that were wrongly extracted by the topic extraction algorithm which normally occurs in Taglish articles.
# I/O : list (array of topics with non_enders) / list (array of topics without non_enders)
def remove_non_enders(topics):
    non_enders = ('po', 'at', 'and', 'because', 'ay', 'but', 'ang', 'sa', 'na', 'mga', 'pero', 'isang', 'o', 'ang', 'kay', 'of', 'nila', 'kung', 'ng', 'sa', 'mga', 'dahil', 'sila', 'ako', 'ko', 'niyo', 'si', 'ngayon', 'nating', 'kanyang', 'pa', 'rin', 'also', 'halos', 'habang', 'i')
    return_topics = []
    for topic in topics:
        flag = False
        for ne in non_enders:
            tokens = topic.split()
            if tokens[len(tokens)-1].lower() == ne:
                flag = True
                break
        if flag:
            if " ".join(tokens[0:len(tokens)-1]) != '':
                return_topics.append(" ".join(tokens[0:len(tokens)-1]))
        else:
            return_topics.append(topic)
    return return_topics

# [in main] this function removes all non-alphanumeric characters on both sides and disregards the non-alphanumeric characters in alphanumeric characters. basically this sets all non-alphanumeric characters on the sides into "*" then strip it later for removal.
# I/O : list (array of topics) / list (array of cleaned topics)
def clean_topics(topics):
    alphabet = list(string.letters) #init from python
    digits = list(string.digits)
    whitelist = [" ", "#", "@"]
    fin_topics = []
    trash_topics = ['This email address', 'Go To Comments']

    for topic in topics:
        if not topic.isalnum():
            temp = ""
            flag = False
            for letter in list(topic):
                if letter in alphabet or letter in digits or letter in whitelist:
                    flag = True
                    temp = temp + letter
                else:
                    if flag == False:
                        temp = temp + "*"
            temp_topic = temp.strip('* ')
            if temp_topic and temp_topic not in trash_topics:
                try:
                    float(temp_topic.replace(' ', ''))
                except ValueError:
                    fin_topics.append(temp_topic)
    return fin_topics

# [in main] this function fixes the Sentence Construction Bug @ Named Entity Detection: Different language conjunctions bug.
# I/O : list (array of topics) / list (array of topics)
# Eg I/O: ['University of the Philippines sa Cebu City sa Marso'] / ['University of the Philippines', 'Cebu City', 'Marso']
def fix_language_conjunction_bug(topics, language):
    tagalog_location = 'package/tagsenttagalognltk/trainingData/'
    english_location = 'package/english/'

    tl_in = open(tagalog_location+'tagalog_prepositions.txt', 'r').read().split('\n')
    tl_cc = open(tagalog_location+'tagalog_conjunctions.txt', 'r').read().split('\n')

    en_in = open(english_location+'english_prepositions.txt', 'r').read().split('\n')
    en_cc = open(english_location+'english_conjunctions.txt', 'r').read().split('\n')

    en_connectors = en_in
    en_connectors.extend(en_cc)

    tl_connectors = tl_in
    tl_connectors.extend(tl_cc)

    to_be_checked = []

    # this loops checks if the topic has conjunctions in different languages. Applicable in Tagalog and English.
    for topic in topics:
        tokens = topic.split()
        languages = []
        for token in tokens:
            if token in en_connectors:
                languages.append('en')
            elif token in tl_connectors:
                languages.append('tl')
        if len(list(set(languages))) > 1:
            to_be_checked.append(topic)

    to_be_added = []

    for tbc in to_be_checked:
        topics.remove(tbc) #remove the to be checked topics first from the main list of topics. add them back later.
        cropped = ""
        tokens = tbc.split()
        if language == "en":
            language_connectors = tl_connectors
        elif language == "te":
            language_connectors = en_connectors
        topics_inside = []
        for token in tokens:
            if token in en_connectors or token in tl_connectors: #just to check if the token is a connector
                if token in language_connectors:
                    cropped = cropped + token + " "
                else:
                    topics_inside.append(cropped)
                    cropped = ""
            else:
                cropped = cropped + token + " "
        topics_inside.append(cropped)
        to_be_added.extend(topics_inside)

    for tba in to_be_added:
        topics.append(tba)

    return topics
# [in main] removes unnecessary prepositions or conjunctions
# applicable for Tagalog topic phrases that were extracted like : "Inihayag ni Tess Delgado", "Sinisi ni Marcos", etc.
# I/O: list (array of topics) /list (array of topcics)
# Eg I/O : ['Sinisi ni Marcos', 'Inihayag ni Tess Delgado'] / ['Marcos', 'Tess Delgado']
def remove_unnecessary_in(topics):
    unnecessary_in = ['ni']
    to_be_checked = []
    for topic in topics:
        index = 0
        for token in topic.split():
            if token in unnecessary_in:
                to_be_checked.append((topic, index))
                break
            index = index + 1

    for tbc in to_be_checked:
        topics.remove(tbc[0]) #remove them first, add them back later
        tokens = tbc[0].split()
        topics.append(" ".join(tokens[tbc[1]+1: len(tokens)]))
    return topics