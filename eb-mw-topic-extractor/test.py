import sys
import os

pathname = os.path.dirname(__file__)        
fullpath = os.path.abspath(pathname) 

nltk_dir = fullpath+"/site_packages/"
# print nltk_dir
sys.path.append(nltk_dir)

import json
from metawhale_topics import mt_index

from lambda_function import lambda_handler 
file_object = open('article_text.txt','r')

para = file_object.read()
# para = "In the schools are enclosed rooms."
para = para.decode('string_escape')

data = {}
data["title"] = "New sugar block farms would soon rise in various provinces as a result of a memorandum of understanding signed among three government agencies. "
data['text'] = para

print lambda_handler(data, True)