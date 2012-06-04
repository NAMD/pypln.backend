#-*- coding:utf-8 -*-
"""
Apply the clustering
"""

from nltk import clean_html
from nltk import TextCollection
from nltk.corpus import stopwords
from BeautifulSoup import BeautifulStoneSoup
from pymongo import Connection
from pymongo.errors import OperationFailure
from math import log
from collections import defaultdict


def build_TC(db, collection):
    #TODO: get configuration from another place
    col = Connection('127.0.0.1')[db][collection]
    #TODO: change to ['analysis']['text']
    tc = TextCollection([t for t in col.find(fields=['text'])], name=collection)
    return tc

def idf(term, corpus):
    term = term.lower()
    texts_with_term = 0
    for text in corpus:
        lower_tokens = [token.lower() for token in text['analysys']['tokens']]
        if term in lower_tokens:
            texts_with_term += 1
    try:
        return 1.0 + log(float(len(corpus)) / texts_with_term)
    except ZeroDivisionError:
        return 0

def tf_idf(term, doc, corpus):
    """Return the tf_idf for a given term"""
    try:
        tfidf = doc['analysis']['freqdist'][term] / idf(term, corpus)
    except KeyError:
        tfidf = 0
    return tfidf

def calculate_distance(host='127.0.0.1', port=27017, db='test',
                       collection='Docs', fields=['text'], query_terms=[]):
    #TODO: get configuration from a file
    conn = Connection(host=host, port=port)
    coll = conn[db][collection]
    query_scores = defaultdict(lambda: 0)
    corpus = list(coll.find({}, fields=['text', 'filename', 'freqdist']))
    for term in [t.lower() for t in query_terms]:
        for doc in corpus:
            score = tf_idf(term, doc, corpus)
            query_scores[doc['_id']] += score
