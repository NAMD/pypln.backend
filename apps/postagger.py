#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
Part of speech tagger based on NLTK
Created on 27/09/11
by flavio
"""
__author__ = 'flavio'
__docformat__ = "restructuredtext en"


from nltk import pos_tag, word_tokenize
from nltk.data import LazyLoader
from nltk.tag import tuple2str
from pymongo import Connection
import argparse
from pypln.workers.tagger_worker import POSTaggerWorker
from pypln.sinks.mongo_update_sink import MongoUpdateSink
from pypln.servers.ventilator import Ventilator
from pypln.servers.baseapp import TaskVentilator

eng_sent_tokenizer = LazyLoader('tokenizers/punkt/english.pickle')
port_sent_tokenizer = LazyLoader('tokenizers/punkt/portuguese.pickle')



def tag_collection(host='127.0.0.1',port=27017,db='test',collection='Docs',fields=['text','lang']):
    """
    POS tag an entire colection of texts on a database
    """
    conn = Connection(host=host,port=port)
    coll = conn[db][collection]
    i = 1
    cursor = coll.find({'tagged_text':None},fields=fields)
    rd = cursor.count()
    print "%s documents need tagging"%rd
    msgs = []
    for t in cursor:
#        print "updating %s of %s"%(i,rd)
        lang = 'en' if 'lang' not in t else t['lang']
        msgs.append({'database':db,'collection':collection,'text':t['text'],'lang':lang,'_id':t['_id']})
#        tt = tag_text(t['text'], lang)
#        try:
#            coll.update({'_id':t['_id']},{'$set':{"tagged_text":tt}})
#        except OperationFailure:
#            print "failed updating document: %s"%t['_id']
#        i +=1
    if msgs:
        vent.push_load(msgs)


def tag_text(text, lang='en'):
    """
    Receives raw text and returns tagged text in the  format word/tag
    """
    if lang == 'en':
        sents = eng_sent_tokenizer.tokenize(text)
    elif lang == 'pt':
        sents = port_sent_tokenizer.tokenize(text)
    tokens = []
    for s in sents:
        tokens.extend(pos_tag(word_tokenize(s)))
    return ' '.join([tuple2str(t) for t in tokens])

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Perform POS tagging on a database collection')
    parser.add_argument('--db', '-d', help="Database",required=True)
    parser.add_argument('--col', '-c', help="Collection",required=True)
    parser.add_argument('--host', '-H', help="Host")
    parser.add_argument('--port', '-p', help="Host")
    parser.add_argument('--field', '-f', help="Host")
    args = parser.parse_args()#    print args, args.prune

    ports = {'ventilator':(5557,5559,5559), # pushport,pubport,subport
        'worker':(5564,5561,5563),          # pushport,pullport,subport
        'sink':(5564,5563,5562)   # pullport,pubport,subport
        }

    tv = TaskVentilator(Ventilator,POSTaggerWorker,MongoUpdateSink,10,ports)
    vent, ws, sink = tv.spawn()
    tag_collection(db=args.db,collection=args.col)
