from __future__ import print_function

import sys
import os

pathname = os.path.dirname(__file__)        
fullpath = os.path.abspath(pathname) 

nltk_dir = fullpath+"/site_packages/"
# print nltk_dir
sys.path.append(nltk_dir)


import json
from metawhale_topics import mt_index


def lambda_handler(event, context):

    print('Loading function')
    #print("Received event: " + json.dumps(event, indent=2))
    fin_topics = mt_index(event['title'],event['text'])

    return fin_topics
