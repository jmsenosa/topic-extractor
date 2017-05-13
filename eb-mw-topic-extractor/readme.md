#Topic Extraction

##Adding packages from pip

`pip install --target=\site_packages package_name`

**PIP Dependencies**

* langdetect
* pyenchant
* bottle

###Importing dependencies

####[langdetect](https://pypi.python.org/pypi/langdetect) example: 

```
#!python

import site_packages.langdetect as langdetect
langdetect.detect("War doesn't show who's right, just who's left.")

```

##Adding nltk_data

**How to change download directory in nltk:
In command line:**


1. `python`
2. `import nltk`
3. `nltk.download()`

A window would launch then click on File>Change Download Directory to <project_directory>/package/nltk_data.

**NLTK Dependencies**

* Corpora > words
* Corpora > wordnet
* Model > punkt
* Model > averaged_perceptro
  n_tagger
* Model > maxent_ne_chunker

###Adding the changed download directory on python:

```
#!python

import nltk

project_dir = os.path.dirname(__file__)
nltk_dir = project_dir+"/package/nltk_data"
nltk.data.path.append(nltk_dir)

```

##Testing

1. Run `python webserver1.py` to launch a server. Go to http://localhost:8000/ to check if server is running. A text containing "Topic Extractor" would be shown in the browser.
2. Create a POST request to http://localhost:8000/ with an article in json format as the body of the request.

**NPM Dependencies**

* async
* request
* python-shell

##Installing topic-extractor to server

**1. create folder: "topic-extractor"**

**2. installing pip**
    1. sudo apt-get update
    2. sudo apt-get -y install python-pip
    3. pip --help
    4. pip -V


**3. Installing numpy**
    1. install python virtualenv
    2. sudo apt-get install python-dev
    2. export LC_ALL=C
    5. activate virtualenv
    6. pip install --upgrade setuptools
    7. pip install -U numpy
    8. installing bottle
        1. install bottle 
    9. deactivate from env



**4. installing uwsgi**
    sudo apt-get uwsgi uwsgi-plugin-python python-bottle nginx


** sudo apt-get install zip unzip***

* addtional ubuntu packages
*note: install all pip packages inside virtual dev*

##Adding entries to custom_dictionary via API

A. POST /add_dictionary

```
#!json

{   
    "language" : "en", 
    "entries": {
        "once": "RB"
    }
}   
```

Available languages are English (en) and Tagalog (tl) so far. 

Please see the [list of part-of-speech tags used in the Penn Treebank Project](http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html) that is also used for the dictionary.

B. Run `python migrate_dictionary.py` to implement changes on the main dictionary.