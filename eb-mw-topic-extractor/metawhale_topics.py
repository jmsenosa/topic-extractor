# coding=utf-8

#import python packages
import sys, os, logging, warnings, re, time, json, pickle

import site_packages.nltk as nltk

project_dir = os.path.dirname(__file__)
package_dir = project_dir+"/site_packages"
nltk_dir = project_dir+"/package/nltk_data"


sys.path.append(package_dir)
nltk.data.path.append(nltk_dir)

reload(sys)
logging.basicConfig()
sys.setdefaultencoding('utf8')
warnings.filterwarnings('error', category = UnicodeWarning) #converts warning to error


#importing site_packages & nltk
import site_packages.langdetect as langdetect
from nltk.util import ngrams

#importing nlp algorithms
from metawhale_topics_functions import * 
import acronymfinder as af
import determine_duplicates as dd
import determine_nuisance_topics as dn
import pos_tagger, data
import scoring
import sentence_construction
import sentence_splitter as ss
import text_preprocessing as tp
import wordfeatures as wf

wordnet_funct = None

def mt_index(title, text): 

    # variable initizalization
    acronyms         = []
    classifier       = pickle.load(open("package/languagedetector.pickle"))
    common_nouns     = []
    final            = []
    final_score      = []
    for_checking     = []
    pos_scores       = []
    tagged_sentences = []

    # text preprocessing
    text = tp.fix(text)  #utf8 encoding fix
    text = tp.trashremove(text) #trash parts removal
    text = tp.contraction(text) #contraction expansion

    # Extracting named entities using sentence construction
    pos_class = pos_tagger.PosTaggerClass(wordnet_funct)
    try:
        tagged_sentences,named_entities = pos_class.generateNamedEntities(text)
    except UnicodeDecodeError:
        tagged_sentences,named_entities = pos_class.generateNamedEntities(text.decode('utf-8'))
    except UnicodeEncodeError:
        tagged_sentences,named_entities = pos_class.generateNamedEntities(text.encode('utf-8'))
    except langdetect.lang_detect_exception.LangDetectException:
        print "No valuable topics in this text."
        sys.exit()

    # Extracting named entities using word features
    # getting the POS of the words then getting the named entities by checking the POS combination
    try:
        extracted_topics = wf.checkerpos(wf.getpos(tagged_sentences)) #getpos function alters some tags from pos tagger to be used for checkerpos function to check the extracted topics
    except IndexError:
        extracted_topics = []

    # getting all topics that are tagged as nn (common nouns) & acronym
    for ch in extracted_topics:
        nn = ch.find('_nn', len(ch)-3)
        acronym = ch.find('_acronym', len(ch)-8)

        if nn != -1:
            common_nouns.append(ch[0:nn])
        elif acronym != -1:
            acronyms.append(ch[0:acronym])

    # checking if the named entities extracted are valid by checking their frequency count
    sentences = ss.sentence_splitter(text) #sentence splitter - text splitted into sentencess
    cn_freq_count = scoring.frequency_count(common_nouns, sentences)
    for cn in cn_freq_count:
        if cn[1] > 1:
            final.append((cn[0], 3))

    # extracting named entities by getting the meaning of the acronyms present on the text
    for acronym_meaning in af.getacronymmeaning(acronyms, text):
        final.append((acronym_meaning, 2))

    # getting the social tokens
    for stk in getsocialtokens(text):
        final.append((stk, 2))

    # adding the named entities from sentence construction algorithm to final set of topics
    for named_entity in named_entities:
        try:
            final.append((' '.join(named_entity.split()), 1))
        except AttributeError:
            final.append((' '.join(named_entity), 1))

    # sorts the topic by it's score
    x = sorted(final, key=lambda kw: kw[1])
    for xx in final:
        if xx[0]:
            for_checking.append(xx[0].strip())

    for_checking = list(set(for_checking))

    # nuisance topics detection
    try:
        tokens = nltk.word_tokenize(text)
    except UnicodeDecodeError:
        tokens = nltk.word_tokenize(text.decode('utf-8'))
        # languages = langdetect.detect_langs(text.decode('utf-8'))
    except UnicodeEncodeError:
        tokens = nltk.word_tokenize(text.encode('utf-8'))
        # languages = langdetect.detect_langs(text.encode('utf-8'))

    feats = dict([(token, True) for token in tokens])
    language = classifier.classify(feats)

    tl = json.loads(open('custom_dictionary/tl.json').read())
    en = json.loads(open('custom_dictionary/en.json').read())
    if language == "te":
       tl.update(en)
       nuisance_dict = tl
    elif language == "en":
        nuisance_dict = en
    else:
        nuisance_dict = []

    for_checking = dn.fix_language_conjunction_bug(for_checking, language)
    for_checking = dn.clean_topics(for_checking)
    for_checking = dn.remove_non_enders(for_checking)
    for_checking = dn.nuisance_removal(for_checking, nuisance_dict)
    for_checking = dn.remove_unnecessary_in(for_checking)

    # frequency count
    topic_freq_count = scoring.frequency_count(for_checking, sentences) # topic_freq_count is an array of lists with the format[(topic1, frequency1), (topic2, frequency2)]
    # POS scoring
    pos_scores = scoring.pos_scoring(topic_freq_count, tagged_sentences)
    # position scores
    position_scores = scoring.position_scoring(topic_freq_count, sentences, title)


    for i in range(0, len(topic_freq_count)):
        # 50 % pos_scores  # 30 % position  # 20 % freq_count
        score = 0
        score = (pos_scores[i][1] * .50) + (position_scores[i][1] *.30) + (topic_freq_count[i][1] * .20)
        final_score.append((topic_freq_count[i][0].strip(), topic_freq_count[i][1] ,score))

  # determining duplicate topics
    fin_topics = dd.determine_duplicates(final_score, text)

    list_topics = []
    for f in fin_topics:
        list_topics.append(fin_topics[f])

    fin_topics = sorted(list_topics, key=lambda kw: kw['score'], reverse = True)

    return fin_topics