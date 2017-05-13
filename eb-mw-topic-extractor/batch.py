# -*- coding: utf-8 -*-

from lambda_function import lambda_handler
import sys
article = {}
article['text']  = sys.argv[1]
article['title'] = sys.argv[2]

topics = lambda_handler(article, True)

for f in topics:
  if f['frequency_count'] > 0:
    print f["topic"]
    print f["frequency_count"]
    print f['score']
    print str(len(f["aliases"]))
    for alias in f["aliases"]:
      print alias

sys.exit()