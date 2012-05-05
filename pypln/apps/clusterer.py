#-*- coding:utf-8 -*-
"""
Applies the clustering

Created on 10/10/11
by Flavio Codeço Coelho
"""

__author__ = 'flavio'

from nltk import clean_html
from nltk import TextCollection
from nltk.corpus import stopwords
from BeautifulSoup import BeautifulStoneSoup
from pymongo import Connection
from pymongo.errors import OperationFailure
from math import log
from collections import defaultdict

def build_TC(db, collection):
    col = Connection('127.0.0.1')[db][collection]
    tc = TextCollection([t for t in col.find(fields=['text'])], name=collection)
    return tc

def idf(term,corpus):
    num_texts_with_term = sum([int(term.lower() in text['text'].lower().split()) for text in corpus])
    try:
        return 1.0 +log(float(len(corpus))/num_texts_with_term)
    except ZeroDivisionError:
        return 0

def tf_idf(term,doc,corpus):
    """
    Returns the tf_idf for a given term
    """
    try:
        tfidf = dict(doc['freqdist'])[term]/idf(term,corpus)
    except KeyError:
        tfidf = 0
    return tfidf

def calculate_distance(host='127.0.0.1',port=27017,db='test',collection='Docs',fields=['text'], query_terms=[]):
    conn = Connection(host=host,port=port)
    coll = conn[db][collection]
    query_scores = defaultdict(lambda:0)
    corpus = list(coll.find({},fields=['text','filename','freqdist']))
    for term in [t.lower() for t in query_terms]:
        for doc in corpus:
            score = tf_idf(term,doc,corpus)
            print 'TF-IDF(%s): %s'%(doc['filename'],term), score
            query_scores[doc['_id']] += score
    for d,s in sorted(query_scores.items()):
        print d,s



if __name__=="__main__":
    calculate_distance(db='Results',collection='Documentos',query_terms=['dengue', 'math'])
