# -*- coding: utf-8 -*-
import site_packages.nltk as nltk
import re
import sys
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class NameEntityRecognizer(object):

    ne_Person     = []
    nameEntity    = []
    nameEntityObj = []

    def __init__(self):
        return


    """ Extract passed parts of speech list """
    def pos_extractor(self, text):
        try:
            tokens = nltk.word_tokenize(text)
        except UnicodeDecodeError:
            tokens = nltk.word_tokenize(text.decode('utf-8'))
        except UnicodeEncodeError:
            tokens = nltk.word_tokenize(text.encode('utf-8'))

        tokens = nltk.pos_tag(tokens)
        tree = nltk.ne_chunk(tokens)
        # tree.draw() # Draws the tree structure for us

        ne_indexer = []
        ne_list = []


        counter = 0
        for subtree in tree:

            if type(subtree) is nltk.Tree:

                ne_indexer.append({
                    'index'     : counter,
                    'nodelabel' : subtree.label(),
                    'nodePOS'   : subtree[0][1],
                    'nodeValue' : subtree[0][0]
                })

                self.nameEntity.append(subtree[0][0])
                ne_list.append(subtree[0][1])

                if subtree.label() == "PERSON":
                    self.ne_Person.append(subtree[0][0])

            counter = counter + 1

        self.nameEntityObj = ne_indexer


    def checkhumanEntities(self,entities):

        newEntities = []

        for namedentity in entities:
            and_search = None

            try:
                and_search = re.search('(?:and)', namedentity)
            except:
                pass

            if and_search is None:
                newEntities.append(namedentity)
            else:
                entity_withand = namedentity.split()
                ind = 0
                try:
                    ind = entity_withand.index("and")
                except:
                    pass

                _pnames = []

                for x in xrange(0,len(entity_withand) - 1):
                    if entity_withand[x] in self.ne_Person:
                        _pnames.append(x)

                if all(i >= ind for i in _pnames) == False:
                    humans = namedentity.split("and")
                    for human in humans:
                        newEntities.append(human.strip())
                else:
                    newEntities.append(namedentity)

        entities = newEntities
        newEntities = []

        return entities
        # return entities



