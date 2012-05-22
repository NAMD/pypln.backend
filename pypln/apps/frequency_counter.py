#-*- coding:utf-8 -*-
"""
This script
Created on 28/09/11
by flavio
"""
__author__ = 'flavio'

from nltk import ConditionalFreqDist, FreqDist, word_tokenize
from nltk.data import LazyLoader
from pymongo import Connection
from pymongo.errors import OperationFailure
import cPickle
import argparse
from collections import OrderedDict
from bson import BSON
from bson.son import SON

#tokenizer = {'en':LazyLoader('tokenizers/punkt/english.pickle'),
#             'pt':LazyLoader('tokenizers/punkt/portuguese.pickle')}

#TODO: implement the possibility to run as a single process or to call workers to do the work in parallel

def frequency(host='127.0.0.1',port=27017,db='test',collection='Docs',fields=['text']):
    """
    Calculate frequency distribution (dictionary) of words of each document of the collection and store it
    as a list of items.

    """
    conn = Connection(host=host,port=port)
    coll = conn[db][collection]
    i = 1
    cursor = coll.find({"freqdist":None},fields=fields+['lang'])
    rd = cursor.count()
    print "%s  documents need analysis"%rd
    for t in cursor:
        print "updating %s of %s"%(i,rd)
        lang = 'en' if 'lang' not in t else t['lang']
        fd = FreqDist(word_tokenize(t['text']))#.encode('utf8')))
        try:
            di = OrderedDict(fd).items()
            coll.update({'_id':t['_id']},{'$set':{"freqdist":di}})#cPickle.dumps(fd)
        except OperationFailure:
            print "failed updating document: %s"%t['_id']
        i +=1

def conditional_frequency(text):
    pass

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Perform word frequency analysis on a database collection')
    parser.add_argument('--db', '-d', help="Database")
    parser.add_argument('--col', '-c', help="Collection")
    parser.add_argument('--host', '-H', help="Host")
    parser.add_argument('--port', '-p', help="Host")
    parser.add_argument('--field', '-f', help="Host")
    args = parser.parse_args()

    #frequency(db='Results',collection='Documentos')
    frequency(db=args.db,host=args.host,port=args.port,collection=args.col,fields=args.field)
