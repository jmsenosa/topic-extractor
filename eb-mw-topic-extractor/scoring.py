# coding=utf-8
from metawhale_topics_functions import find_term, remove_unnecessary_year_word_combination
from nltk.util import ngrams
import nltk, re

def pos_scoring(topic_freq_count, tagged_sentences):
    pos_scores = []
    for topic in topic_freq_count:
        named_entity = topic[0]
        for entity_token in named_entity.split():
            pass_ = False
            try:
                tagged_sentences[0]
            except IndexError:
                pos_scores.append((named_entity, 1))
                break
            for index in range(0, len(tagged_sentences[0])):
                if tagged_sentences[0][index][0] == entity_token:
                    combination = ""
                    possible_score = 0
                    for i in range(index, index+len(named_entity.split())):
                        try:
                            combination = combination + tagged_sentences[0][i][0]+" "
                            if tagged_sentences[0][i][1] == 'NNP' or tagged_sentences[0][i][1] == 'NNPS':
                                possible_score = possible_score + 3
                            elif tagged_sentences[0][i][1] == 'NN' or tagged_sentences[0][i][1] == 'NNS':
                                possible_score = possible_score + 2
                            else:
                                possible_score = possible_score + 1
                        except IndexError:
                          pass

                    if combination.strip() == named_entity:
                        pos_scores.append((named_entity, possible_score))
                        pass_ = True
                        break
            if pass_:
                break
            if entity_token == named_entity.split()[len(named_entity.split())-1] and not pass_:
                pos_scores.append((named_entity, 1))
    return pos_scores

def position_scoring(topic_freq_count, sentences, title):
    position_scores = []
    sentences_len = len(sentences)
    first_len = sentences_len/3
    second_len = first_len * 2

    first_part = " ".join(sentences[0:first_len])
    second_part = " ".join(sentences[first_len:second_len])
    third_part = " ".join(sentences[second_len:sentences_len])

    position_scores = []

    for topic in topic_freq_count:
        score = 0
        if find_term(first_part, topic[0]):
            score = score + 3
        if find_term(second_part, topic[0]):
            score = score + 2
        if find_term(third_part, topic[0]):
            score = score + 1
        if find_term(title, topic[0]):
            score = score + 4
        position_scores.append((topic[0], score))
    return position_scores


# [in main] frequency_count gets the frequency count of each topic in the given text. I/O: two params (list, list) - (string - list of topics, sentences - list of sentences in the given text. should be a product of sentencesplitter()) / list of tuple - format: [(topic1, frequency1), (topic2, frequency2)]
def frequency_count(topics, sentences):
    # text should be modified in sentence segmentation
    fin = []
    for topic in topics: #iteration
        topiclen = len(topic.split())
        ctr = 0
        if topic.startswith(('#', '@')):
            for sentence in sentences:
                sentence = re.sub('[^0-9a-zA-Z@# ]+', '', sentence)
                try:
                    tokens = sentence.split()
                except UnicodeDecodeError:
                    tokens = sentence.decode('utf-8').split()
                except UnicodeEncodeError:
                    tokens = sentence.encode('utf-8').split()
                n_grams = list(ngrams(tokens, topiclen))
                for n in n_grams:
                    try:
                        if topic.split() == list(n):
                            ctr = ctr + 1
                    except UnicodeWarning:
                        pass
        else:
            for sentence in sentences:
                try:
                    tokens = nltk.word_tokenize(sentence)
                except UnicodeDecodeError:
                    tokens = nltk.word_tokenize(sentence.decode('utf-8'))
                except UnicodeEncodeError:
                    tokens = nltk.word_tokenize(sentence.encode('utf-8'))
                n_grams = list(ngrams(tokens, topiclen))
                for n in n_grams:
                    try:
                        if topic.split() == list(n):
                            ctr = ctr + 1
                    except UnicodeWarning:
                        pass
        fin.append([topic, ctr])
    fin = remove_unnecessary_year_word_combination(fin)
    return fin