#!/usr/bin/python
# -*- coding: utf-8 -*-
import pos_tagger
import sys
import json
from package.tagsenttagalognltk import pos_tagging

posClass = pos_tagger.PosTaggerClass()
tl_posTagger = pos_tagging.POS_tagger()

para = ''

file_object = open('article_text.txt','r')


para = file_object.read()
# para = "In the schools are enclosed rooms."
para = para.decode('string_escape')

tagged_sentences,nameEndtities = posClass.generateNamedEntities(para)


for taggeds in tagged_sentences:
    # for tagged in taggeds:
    print taggeds 

for nameEndtiti in nameEndtities:
    print nameEndtiti