# import names
from random import choice, randint
from uuid import uuid4
from datetime import datetime
import requests
import classifier
import json
import os

with open('keywords.json') as f:
    query_kw = json.load(f)


def timestamp():
    return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')

def classify(query, text):
    keywords = query_kw[query]
    for kw in keywords:
        if requests.post('http://localhost:5051/classify', json.dumps(dict(hashtag=kw, description=text))).text == 'true':
            return True
    return False

def makedirs(outputDir):
    dirs = ['training_phase_2', 'testing_phase_1', 'intervention', 'testing_phase_2']
    for dir in dirs:
        dir = os.path.join(outputDir, dir)
        if not os.path.exists(dir):
            os.makedirs(dir)