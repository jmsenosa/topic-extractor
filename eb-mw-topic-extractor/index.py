from bottle import Bottle, run, route,  get, post, request, response, template
import json

application = app = Bottle()

from json import dumps
# from threader import topicExtractorThreading
import sys
import os

pathname = os.path.dirname(__file__)
fullpath = os.path.abspath(pathname)

import json
from metawhale_topics import mt_index

import Queue
queut = Queue.Queue()

nltk_dir = fullpath+"/site_packages/"
sys.path.append(nltk_dir)


@app.get('/')
def home():
    return "Topic Extractor"

@app.post('/') # or @route('/login', method='POST')
def extract_topics():
    response.content_type = 'application/json'
    request.json

    # article_id = request.json['_id']
    text = request.json['text']
    title = request.json['title']

    try:
        queut.put(mt_index(title, text))

        while not queut.empty():
            return dumps(queut.get())
    except:
        errex = {};
        errex['status'] = 'error'
        errex['message'] = 'Contact the administrator.'
        return dumps(errex)

@app.post('/add_dictionary')
def add_dictionary():
    response.content_type = 'application/json'
    request.json
    return_message = {}
    dictionary_entries = request.json['entries']
    language = request.json['language']
    fileLoc = 'custom_dictionary/'+language+'.json'
    try:
        dictionary = json.loads(open(fileLoc).read())

    except IOError: # IOError in opening the file
        return_message['result'] = "error"
        return_message['message'] = "No language support for "+language+" language."
        return return_message

    data = {}
    temp = json.loads(open('custom_dictionary/temp.json').read())
    try:
        dictionary.update(temp[language])
    except KeyError:
        return_message['result'] = "error"
        return_message['message'] = "No language support for "+language+" language."
        return return_message

    for entry in dictionary_entries:
        try:
            dictionary[entry]
            data[entry] = "existing"
        except KeyError:
            temp[language][entry] = dictionary_entries[entry]
            data[entry] = "added"

    with open('custom_dictionary/temp.json', 'w') as outfile:
        json.dump(temp, outfile)

    return_message['result'] = "ok"
    return_message['count'] = len(data)
    return_message['data'] =dict(sorted(data.items()))
    return return_message



class StripPathMiddleware(object):
    '''
    Get that slash out of the request
    '''
    def __init__(self, a):
        self.a = a
    def __call__(self, e, h):
        e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
        return self.a(e, h)

if __name__ == '__main__':
    run(app=StripPathMiddleware(app),
        host='0.0.0.0',
        port=8080)

# run(app, host='0.0.0.0', port=8000, reloader=True) #prod setup
# run(host='localhost', port=8000, debug=True, reloader=True) #dev setup