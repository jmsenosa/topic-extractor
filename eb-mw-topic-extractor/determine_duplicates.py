# coding=utf-8
from __future__ import print_function
from metawhale_topics_functions import find_term, is_not_numeric, honorifics, checkifnum, find_word
from acronymfinder import meaningchecker
import boto3
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb',endpoint_url="https://dynamodb.ap-southeast-1.amazonaws.com")
table = dynamodb.Table('Topics')

## duplicate removal

## --- SURNAME ---- ###

# getsurnames is a function that gets the possible surnames given in a list. it's similar to segregator() since it checks if the topic is composed of one word only or else, but it checks if it suites to be a surname first before adding. so far, two word surnames like "De Vera" can't be detected by this algorithm. used by surname(). I/O: list (topics) / tuple (list, list) - (surnames, not_surnames)
def getsurnames(topics):
    surnames = []
    not_surnames = []
    for topic in topics:
        if len(topic[0].split()) == 1:
            if topic[0].istitle() or topic[0][0].isupper():
                surnames.append(topic)
        else:
            not_surnames.append(topic)
    return (surnames, not_surnames)

# issurname is a function that checks if the given surname is the surname of the given name. for example, if surname is "Aquino" and the given name is "Benigno Aquino", it would return a True. It can deal with name suffixes like "Jr.", "Sr." etc. so if the name is "Benigno Aquino III", it can detect that the "Aquino" surname belongs to that person. I/O: two params (string, string) - (surname, name) / boolean
def issurname(surname, name):
    if name.endswith(('Jr.', 'Sr.', 'II', 'III', 'IV')):
        name = name.split() # name becomes an array
        pos_surname = name[len(name)-2]
    else:
        name = name.split() # name becomes an array
        pos_surname = name[len(name)-1] # pos_surname takes the last value of the array
    if surname == pos_surname:
        return True
    else:
        return False

# surname is a function that segregates the topics into two clusters: the non_surname and surname topics. it returns a tuple of lists. I/O: list (topics) / tuple (list, list of tuple) - (non_surname topics, a list of tuple which contains the surname and the possible surname owners. format is like this: [('Aquino', ['Ninoy Aquino', 'Cory Aquino', 'Kris Aquino']), ('Binay', ['Jejomar Binay'])]
def surname(topics):
    possible_surnames, non_surname = getsurnames(topics)
    sn = []
    for ps in possible_surnames:
        found = False
        dup = []
        for name in non_surname:
            if issurname(ps[0], name[0]):
                dup.append(name)
                found = True
        if not found:
            non_surname.append(ps)
        else:
            sn.append([ps, dup])
    return (non_surname, sn)

# hon_check is a function which checks if the topics starts with a honorific. I/O: string (topic) / tuple (if True - boolean, string (topic), string (honorific) | False - boolean, None, None)
def hon_check(topic):
    found = False
    for honorific in honorifics:
        if topic[0].startswith(honorific):
            found = True
            topic = topic[0].replace(honorific, "").strip()
            pair = (True, topic, honorific)
            break
    if found:
        return pair
    else:
        return (False, None, None)

# present_in is a function if a word is in a topic or name. for example, you want to find "pork barrel" in the sentence "She uses pork barrel" , it would return a True. I/O: two params (string, string) - (word to find, sentence or text) / boolean
def present_in(check, name):
    result = False
    ch = check.split()
    n_grams = list(ngrams(name.split(), len(ch)))
    for ng in n_grams:
        if ch == list(ng):
            result = True
    return result

## -- surname duplicate end -- ##

## -- keyword relationship -- ##

def set_checker(topics):
    # checks if the set of topics are different persons and if same person, combine it.
    highest_score = topics[0]
    debug_messages = []
    duplicates = []

    for topic in topics:
        if highest_score[1] < topic[1]:
            highest_score = topic

    comparing_topics = []

    for topic in topics:
        if topic is not highest_score:
            comparing_topics.append(topic)

    for topic in comparing_topics:
        if find_term(topic[0], highest_score[0]):
            res, sep = find_word(topic[0], ('and', 'AND', 'And'))
            if not res:
                topics.remove(topic)
                debug_messages.append("(f) Removed \""+topic[0]+"\" - duplicate of \""+highest_score[0]+"\"")
                duplicates.append((highest_score[0], topic))
            else:
                debug_messages.append("topic has \'and\' "+topic[0])

    return (debug_messages, topics, duplicates)

# removal_of_almost_the_same_topics is a function for pre-checking the topics' duplicates. I/O : two params (list, list) - (list of tuples in this format: [(topic_name, frequency_count, score)], list of tuples in this format - [(main_topic1, (duplicate1, frequency_count1, score1)), (main_topic2, (duplicate2, fc2, score2))]) /  tuple (topic, certain_duplicates) - (same topic format as the input but without the duplicate, list of duplicate)
def removal_of_almost_the_same_topics(topics, certain_duplicates):
    to_be_removed = []
    ## removal of almost the same topics
    for topic1 in topics:
        for topic2 in topics:
            if not topic1[0] in to_be_removed and not topic2[0] in to_be_removed:
                if not topic1[0] == topic2[0]:
                    if topic1[0] == topic2[0].replace('-',' ') or topic1[0].lower() == topic2[0].lower(): # but the other topic has extra characters (eg. P25-billion & P25 billion)
                        if topic1[0].isupper() or topic1[0].islower():
                            to_be_removed.append(topic1[0])
                        else:
                            to_be_removed.append(topic2[0])
                    # eg. Marikina City and Marikina - Marikina will be removed
                    if find_term(topic2[0].lower(), 'city') and topic1[0].lower() == topic2[0].lower().replace('city', '').strip():
                        to_be_removed.append(topic1[0])
                        certain_duplicates.append((topic2[0], topic1))
                    # eg. The Marcos and Marcos - The Marcos will be removed
                    if find_term(topic2[0].lower(), 'the') and topic1[0].lower() == topic2[0].lower().replace('the', '').strip() and topic2[0].startswith("The"):
                        to_be_removed.append(topic2[0])
                        certain_duplicates.append((topic1[0], topic2))
                    # eg. Ang Liberal Party and Liberal Party - Ang Liberal Party will be removed.
                    if find_term(topic2[0].lower(), 'ang') and topic1[0].lower() == topic2[0].lower().replace('ang', '').strip() and topic2[0].startswith("Ang"):
                        to_be_removed.append(topic2[0])
                        certain_duplicates.append((topic1[0], topic2))
                    # eg. PUV and PUVs - PUVs will be removed
                    if topic2[0].endswith('s') and topic2[0][0:len(topic2[0])-1].isupper() and topic2[0][0:len(topic2[0])-1] == topic1[0] :
                        to_be_removed.append(topic2[0])
                        certain_duplicates.append((topic1[0], topic2))
                    # fix for space issues in topics duplicates.
                    if topic1[0].lower().replace(' ', '') == topic2[0].lower():
                        to_be_removed.append(topic1[0])
                    if topic1[0] == topic2[0].replace('#', ''):
                        if topic1[0].startswith(('#')):
                            to_be_removed.append(topic2[0])
                            certain_duplicates.append((topic1[0], topic2))
                        else:
                            to_be_removed.append(topic1[0])
                            certain_duplicates.append((topic2[0], topic1))
                    elif topic1[0] == topic2[0].replace('@', ''):
                        if topic1[0].startswith(('@')):
                            to_be_removed.append(topic2[0])
                            certain_duplicates.append((topic1[0], topic2))
                        else:
                            to_be_removed.append(topic1[0])
                            certain_duplicates.append((topic2[0], topic1))
                    elif topic1[0] == topic2[0].replace('-', ''):
                        to_be_removed.append(topic2[0])
                        certain_duplicates.append((topic1[0], topic2))
        # removal of topics that have a length of 1
        if len(topic1[0]) == 1:
            to_be_removed.append(topic1[0])
        # removal of topics that have a frequency count of 0
        if topic1[1] == 0:
            to_be_removed.append(topic1[0])
        # removal of topics that are pure numbers
        if not is_not_numeric(topic1[0]):
            to_be_removed.append(topic1[0])
    # removal of topics in to_be_removed
    for tbr in to_be_removed:
        for topic in topics:
            if topic[0] == tbr:
                tbr = topic
                break
        try:
            topics.remove(tbr)
        except (IndexError, KeyError, ValueError):
            pass
    return (topics, certain_duplicates)

# this duplicate detection process aims to detect two similar topics in a similar use case where the extracted topics have "Pangulong Noynoy Aquino" & "Pangulong Aquino" and there's no "Aquino" surname extracted. Thus, the algorithm before this cannot process these duplicates.
def mapping_out_topics_with_the_same_starting_honorific(topics, certain_duplicates, universal_duplicates):
    honorific_duplicates = {} #init
    duplicates = [] #init

    for topic1 in topics: #looping thru topics
        tokens1 = topic1[0].split() #getting the tokenized version of topic1
        if tokens1[0] in honorifics: #checking if the first word is on the honorifics
            for topic2 in topics: # if yes, loop in thru the topics again
                if topic1 != topic2: # check first if it's not checking the same topic
                    if topic2[0].startswith(tokens1[0]) and topic2[0].endswith(tokens1[len(tokens1)-1]): #check if topic2 is starting & ending with the same word in topic1
                        main = "" #init
                        duplicate = () #init
                        if len(tokens1) < len(topic2[0].split()): #checking if what topic has less tokens. the current assumption is the lesser tokens is the less specific just like "Pangulong Aquino" vs. "Pangulong Noynoy Aquino"
                            main = topic2 #the main would be topic2 since it has more tokens, thus, in our assumption, it's more specific
                            duplicate = topic1 #duplicate is the topic w/ lesser tokens
                        else:
                            main = topic1
                            duplicate = topic2

                        if main and duplicate and main not in duplicates:
                            # checking if there's a value for main & duplicate and if main is not yet in duplicates list
                            # You might be wondering why the key used for the honorific_duplicates json is the duplicate. It's because it's easier to determine if there's a lot of instances of the vague topic.
                            # For example, "Pangulong Aquino" is a vague topic since it's only the surname and position title is described.
                            # So what this snippet does is, it lists all the possible topics that might be "Pangulong Aquino"
                            # format -> honorific_duplicates['Pangulong Aquino'] = [('Pangulong Aquino', freq, score), ('Pangulong Noynoy Aquino', freq, score), ('Pangulong Cory Aquino', freq, score)]
                            try:
                                honorific_duplicates[duplicate[0]].append(main) # append if existing
                                duplicates.append(main) # then append main to the duplicate list
                            except KeyError:
                                honorific_duplicates[duplicate[0]] = []
                                honorific_duplicates[duplicate[0]].append(duplicate)
                                honorific_duplicates[duplicate[0]].append(main)
                                duplicates.append(main)
    for hd in honorific_duplicates: # looping thru honorific_duplicates
        if len(honorific_duplicates[hd]) == 2: # check if there are exactly 2 entities inside honorific_duplicates[hd]
            main = honorific_duplicates[hd].pop()
            duplicate = honorific_duplicates[hd].pop()
            universal_duplicates.append(duplicate[0])
            certain_duplicates.append((main[0], duplicate))
            topics.remove(duplicate)

    return (topics, certain_duplicates, universal_duplicates)

def mapping_out_topics_with_honorific_and_surname_to_main_topic(topics, certain_duplicates, universal_duplicates, debug_messages):
    honorific_duplicates = {} #init
    duplicates = [] #init
    for topic1 in topics:
        for honorific in honorifics:
            if topic1[0].startswith(honorific):
                cropped = topic1[0].split(honorific)[1].strip()
                if len(cropped.split()) == 1:
                    # print "surname ", cropped
                    for topic2 in topics:
                        if cropped != topic2[0] and topic1[0] != topic2[0]:
                            if topic2[0].endswith(cropped):

                                if topic1[0] not in duplicates:
                                    try:
                                        honorific_duplicates[topic1[0]].append(topic2)
                                        duplicates.append(topic2[0])
                                    except KeyError:
                                        honorific_duplicates[topic1[0]] = []
                                        honorific_duplicates[topic1[0]].append(topic1)
                                        honorific_duplicates[topic1[0]].append(topic2)
                                        duplicates.append(topic2[0])

    for hd in honorific_duplicates: # looping thru honorific_duplicates
        if len(honorific_duplicates[hd]) == 2: # check if there are exactly 2 entities inside honorific_duplicates[hd]
            main = honorific_duplicates[hd].pop()
            duplicate = honorific_duplicates[hd].pop()
            universal_duplicates.append(duplicate[0])
            certain_duplicates.append((main[0], duplicate))
            topics.remove(duplicate)
    return (topics, certain_duplicates, universal_duplicates, debug_messages)

# for example, "Poe" and "Grace Poe". "Poe" should be marked as a duplicate of "Grace Poe"
def mapping_out_surname_to_surname_owner(topics, certain_duplicates, universal_duplicates, debug_messages):
    non_surname, sn = surname(topics) #surname is a function that seggregates the one word topic (assumed as a surname) and others
    for s in sn: #looping thru surnames or one word topic
        duplicates = []
        topic_set = [] #all topics to be checked in this iteration (surname + possible duplicates)
        topic_set.append(s[0])
        topic_set.extend(s[1])

        original_topic_set_length = len(topic_set)

        if len(s[1]) > 1: # s[1] is the array of duplicates of the surname which is the s[0]
            # initial removal of nuisance duplicate topics. Like in a topic set where "Manny Pacquiao", "Pacquiao" & "The Pacquiao" topics are extracted. "The Pacquiao" is considered as a nuisance topic. Should be remove to avoid confusing the next algorithms.
            tbr = []
            for dup in s[1]:
                if dup[0] == "The "+s[0][0]:  #if topic starts with "The" and the next word is the surname like in "The Pacquiao"
                    topic_set.remove(dup) # remove this to topic_set
                    certain_duplicates.append((s[0][0], dup)) #add to certain duplicate. "The Pacquiao" should be a duplicate of "Pacquiao"
                    tbr.append(dup) #to be removed topic

            for t in tbr: #looping thru to be removed topics in s[1]
                s[1].remove(t) #remove it

        if len(s[1]) > 1: # s[1] is the array of duplicates of the surname which is the s[0]
            for dup in s[1]: # looping thru the duplicates as dup
                res, cropped, honorific = hon_check(dup)  # res - boolean if it's a honorific; cropped - the string w/o the honorific; honorific - the honorific (obv)
                if res: #if res is true continue
                    try: # to catch a ValueError exception
                        if cropped == s[0][0]: # if the cropped topic is equal the surname (eg. original: "Sen. Poe" cropped = "Poe", surname = "Poe")
                            topic_set.remove(dup)
                            universal_duplicates.append(dup[0])
                            certain_duplicates.append((cropped, dup))
                            debug_messages.append("(a) removed \""+ str(dup[0])+"\" duplicate of \""+cropped+"\"")
                        for s1 in s[1]:
                            if cropped == s1[0]:  #if the cropped topic is equal on one of the duplicates (eg. original: "Senator Grace Poe" cropped = "Grace Poe" and "Grace Poe" is also found in the duplicates)
                                topic_set.remove(s1)
                                certain_duplicates.append((dup[0], s1)) #original , duplicate
                                universal_duplicates.append(s1[0])
                                debug_messages.append("(b) removed \""+ str(s1[0])+ "\", is a cropped duplicate of \""+dup[0]+"\"")
                                break
                    except ValueError: # sometimes there's a value error, must be on removing values from topic_set
                        pass

        if len(topic_set) == original_topic_set_length:
            # this means nothing was removed on the first duplicate removal algorithm
            # this algorithm works for this kind of topic_set where there's only honorific and the surname eg: "Poe" => "Senator Grace Poe" & "Sen. Grace Poe"
            # will result to a new topic where the "cropped" from hon_check (Grace Poe) will be the main topic and all of the topics will be marked as duplicates
            # result: "Grace Poe" => "Poe", "Senator Grace Poe", "Sen. Grace Poe"
            cropped_topics = {}
            for dup in s[1]:
                res, cropped, honorific = hon_check(dup) # get all the cropped version of each topic
                if cropped: # if there's a cropped version, add to cropped_topics object
                    # debug_messages.append("cropped "+str(cropped)+" original "+str(dup))
                    try:
                        cropped_topics[cropped].append(dup) # if there's an existing cropped name, append the original topic
                    except KeyError: # error catcher if there's an existing cropped name
                        cropped_topics[cropped] = [] # create a new cropped name key
                        cropped_topics[cropped].append(dup) # append the original topic

            if cropped_topics:
                for ct in cropped_topics:
                    if len(cropped_topics[ct]) > 1: # if the number of original topics for that cropped key is more than 1, then it must be a valid cropped topic
                        for topic in cropped_topics[ct]:
                            certain_duplicates.append((ct, topic))
                            topic_set.remove(topic)
                            universal_duplicates.append(topic[0])

            if len(topic_set) == 1:
                for ct in cropped_topics:
                    certain_duplicates.append((ct, s[0]))


        if len(topic_set) > 1:
            dm2, topic_set, duplicate_set = set_checker(topic_set[1:len(topic_set)])
            debug_messages.extend(dm2)
            for dupl in duplicate_set:
                universal_duplicates.append(dupl[1][0])
            certain_duplicates.extend(duplicate_set)

        if len(topic_set) <= 1: # if topic is not a duplicate of more than 1 topic
            duplicates.append(s[0]) # add the 'surname' to the list of duplicates.
            universal_duplicates.append(s[0][0])
            try:
                if topic_set[0][0].startswith("The"):
                    certain_duplicates.append((s[0][0], topic_set[0]))
                    debug_messages.append("(c.1) removed \""+ str(topic_set[0][0])+"\" duplicate of surname "+s[0][0]+" topic_set "+str(topic_set))
                    universal_duplicates.append(topic_set[0][0])
                else:
                    certain_duplicates.append((topic_set[0][0], s[0]))
                    debug_messages.append("(c.2) removed the surname \""+ str(s[0][0])+"\" duplicate of "+topic_set[0][0])
                    universal_duplicates.append(s[0][0])
            except ValueError:
                pass
    return (topics, certain_duplicates, universal_duplicates, debug_messages)

def mapping_out_date_duplicates(topics, certain_duplicates, universal_duplicates, debug_messages):
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

    topic_with_months = {}

    for month in months:
        for topic in topics:
            if month == topic[0].split()[0]:
                try:
                    topic_with_months[month].append(topic)
                except KeyError:
                    topic_with_months[month] = []
                    topic_with_months[month].append(topic)

    for topic in topic_with_months:
        month_name = topic
        main_date = ()
        duplicate_date = ()
        if len(topic_with_months[topic]) == 2:
            for duplicate in topic_with_months[topic]:
                if duplicate[0] == month_name:
                    duplicate_date = duplicate
                else:
                    main_date = duplicate
            if main_date and duplicate_date:
                certain_duplicates.append((main_date[0], duplicate_date))
                universal_duplicates.append(duplicate_date[0])
                topics.remove(duplicate_date)
        elif len(topic_with_months[topic]) > 2: # if topic is more than 2, remove the topic with month only | eg: April & April 9 & April 12 & April 2014 => April should be removed
            for duplicate in topic_with_months[topic]:
                if duplicate[0] == topic:
                    removed_topic = topics.remove(duplicate)
                    break
    return (topics, certain_duplicates, universal_duplicates, debug_messages)

# mapping out subwords to main topic. for example, "Ateneo Lady Eagles (main) & Lady Eagles (subword)"
def mapping_out_subwords_to_main(topics, certain_duplicates, universal_duplicates, debug_messages):
    for topic1 in topics:
        tokenized1 = topic1[0].split()
        for topic2 in topics:
            tokenized2 = topic2[0].split()
            if topic1[0] != topic2[0] and len(tokenized1) < len(tokenized2) and len(tokenized1) in (2,3): # this algorithm accepts subwords with 2 and 3 words. This is a tuple, so just add the desired number of words as a subword.
                if topic2[0].endswith(topic1[0]): # check if the main topic ends with the subword
                    certain_duplicate = (topic2[0], topic1)   #orig, duplicate
                    if certain_duplicate not in certain_duplicates: #checking if the duplicate set is existing
                        certain_duplicates.append(certain_duplicate) # adding to certain duplicates if not found
                        universal_duplicates.append(topic1[0]) # always add to universal_duplicates to remove the topic
                elif find_term(topic2[0], topic1[0]):
                    certain_duplicate = (topic2[0], topic1)
                    if certain_duplicate not in certain_duplicates: #checking if the duplicate set is existing
                        certain_duplicates.append(certain_duplicate)
                        universal_duplicates.append(topic1[0])

    return topics, certain_duplicates, universal_duplicates, debug_messages

# [in main]
def determine_duplicates(topics, text): #function for checking duplicate topics
    f_topics = {}
    debug_messages = []
    universal_duplicates = []
    certain_duplicates = []

    for topic in topics:
        try:
            response = table.query(
                KeyConditionExpression=Key('topicName').eq(topic[0].strip())
            )
        except ClientError as e:
            pass
        else:
            if len(response['Items']) == 1:
                if response['Items'][0]['topicType'] == "ALIAS":
                    certain_duplicates.append((response['Items'][0]['mainTopic'], topic))  #orig, duplicate
                    universal_duplicates.append(topic[0])

    topics, certain_duplicates, universal_duplicates = mapping_out_topics_with_the_same_starting_honorific(topics, certain_duplicates, universal_duplicates)
    # print "after mapping_out_topics_with_the_same_starting_honorific", topics

    topics, certain_duplicates, universal_duplicates, debug_messages = mapping_out_topics_with_honorific_and_surname_to_main_topic(topics, certain_duplicates, universal_duplicates, debug_messages)
    # print "after mapping_out_topics_with_honorific_and_surname_to_main_topic", topics

    topics, certain_duplicates, universal_duplicates, debug_messages = mapping_out_surname_to_surname_owner(topics, certain_duplicates, universal_duplicates, debug_messages)
    # print "after mapping_out_surname_to_surname_owner", topics

    topics, certain_duplicates, universal_duplicates, debug_messages = mapping_out_date_duplicates(topics, certain_duplicates, universal_duplicates, debug_messages)
    # print "after mapping_out_date_duplicates", topics

    topics, certain_duplicates, universal_duplicates, debug_messages = mapping_out_subwords_to_main(topics, certain_duplicates, universal_duplicates, debug_messages)
    # print "after mapping_out_subwords_to_main", topics

    # populate the remaining topics into f_topics
    for topic in topics:
        try:
            f_topics[topic[0]]
        except KeyError:
            if topic[0] not in universal_duplicates:
                f_topics[topic[0]] = {}
                content = {}
                content['topic'] = topic[0]
                content['aliases'] = []
                content['frequency_count'] = topic[1]
                content['score'] = topic[2]
                f_topics[topic[0]] = content


    # debug_messages.append("certain_duplicates = "+str(certain_duplicates))

    # mapping out certain duplicates
    to_be_added = []
    for f_topic in f_topics:
        found = False
        for t in certain_duplicates:
            if f_topics[f_topic]['topic'] == t[0]:
                if t[1] not in f_topics[f_topic]['aliases']:
                    f_topics[f_topic]['aliases'].append(t[1])
                    f_topics[f_topic]['frequency_count'] = f_topics[f_topic]['frequency_count'] + t[1][1]
                    f_topics[f_topic]['score'] = f_topics[f_topic]['score'] + t[1][2]
                found = True
                break
            else:
                for topic_dupl in f_topics[f_topic]['aliases']:
                    if topic_dupl[0] == t[0]:
                        if t[1] not in f_topics[f_topic]['aliases']:
                            f_topics[f_topic]['aliases'].append(t[1])
                            f_topics[f_topic]['frequency_count'] = f_topics[f_topic]['frequency_count'] + t[1][1]
                            f_topics[f_topic]['score'] = f_topics[f_topic]['score'] + t[1][2]
                        found = True
                        break

            if not found:
                if t not in to_be_added:
                    to_be_added.append(t)
        if found:
            # certain_duplicates.remove(t)
            break

    # mapping out certain duplicates that aren't in the original f_topics line up
    for tba in to_be_added:
        topic_name = tba[0]
        try:
            if tba[1] not in f_topics[topic_name]['aliases']:
                f_topics[topic_name]['aliases'].append(tba[1])
                f_topics[topic_name]['frequency_count'] = f_topics[topic_name]['frequency_count'] + tba[1][1]
                f_topics[topic_name]['score'] = f_topics[topic_name]['score'] + tba[1][2]
        except KeyError:
            f_topics[topic_name] = {}
            f_topics[topic_name]['topic'] = topic_name
            f_topics[topic_name]['aliases'] = []
            f_topics[topic_name]['aliases'].append(tba[1])
            f_topics[topic_name]['frequency_count'] = tba[1][1]
            f_topics[topic_name]['score'] = tba[1][2]


    ## duplicate in organization name & organization acronym
    acronyms = []
    non_acronyms = []

    for f_topic in f_topics:
        topic_name = f_topic.strip()
        if topic_name.isupper() and not checkifnum(topic_name) and not find_word(topic_name, ('million', 'billion', 'percent', 'trillion', 'hectares'))[0]:
            acronyms.append(f_topics[f_topic])
        elif topic_name[len(topic_name)-1] == "s":
            if topic_name[0:len(topic_name)-1].isupper():
                acronyms.append(f_topics[f_topic])
            else:
                non_acronyms.append(f_topics[f_topic])
        else:
            non_acronyms.append(f_topics[f_topic])

    for acronym in acronyms:
        acronym_name = acronym['topic'].strip()
        for non_acronym in non_acronyms:
            non_acronym_name = non_acronym['topic'].strip()

            if acronym_name.endswith('s'):
                res, meaning = meaningchecker(non_acronym_name.split(), acronym_name.replace('s',''))
            else:
                res, meaning = meaningchecker(non_acronym_name.split(), acronym_name)

            if acronym_name == "SC" and non_acronym_name == "Supreme Court":
                res, meaning = meaningchecker(non_acronym_name.split(), acronym_name)

            if res:
                if meaning == non_acronym_name:
                    removed = f_topics.pop(acronym['topic'])
                    universal_duplicates.append(acronym_name)
                    f_topics[non_acronym['topic']]['frequency_count'] = non_acronym['frequency_count'] + acronym['frequency_count']
                    f_topics[non_acronym['topic']]['score'] = non_acronym['score'] + acronym['score']
                    duplicate_to_be_added = (removed['topic'], removed['frequency_count'], removed['score'])
                    if duplicate_to_be_added not in f_topics[non_acronym['topic']]['aliases']:
                        f_topics[non_acronym['topic']]['aliases'].append(duplicate_to_be_added)
                    if removed['aliases']:
                        f_topics[non_acronym['topic']]['aliases'].extend(removed['aliases'])
                    debug_messages.append("(d) added \""+acronym_name+"\" as a duplicate of \""+ non_acronym['topic']+"\"")
                    break

    # last checking

    for duplicate in universal_duplicates:
        try:
            added_duplicate = f_topics.pop(duplicate)
            main = ""
            for cd in certain_duplicates:
                if duplicate == cd[1][0]:
                    main = cd[0]
                    break
            if main:
                for f_topic in f_topics:
                    if f_topic == main:
                        for ad in added_duplicate['aliases']:
                            if ad not in f_topics[f_topic]['aliases']:
                                f_topics[f_topic]['aliases'].append(ad)
                                f_topics[f_topic]['frequency_count'] = f_topics[f_topic]['frequency_count'] + ad[1]
                                f_topics[f_topic]['score'] = f_topics[f_topic]['score'] + ad[2]
                        break
        except KeyError:
            pass

    # print len(debug_messages)
    # for dm in debug_messages:
    #     print dm

    for f_topic in f_topics:
        aliases = []
        if f_topics[f_topic]['aliases']:
            for alias in f_topics[f_topic]['aliases']:
                aliases.append(alias[0])
        f_topics[f_topic]['aliases'] = aliases

    return f_topics
