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
from pypln.logger import make_log

eng_sent_tokenizer = LazyLoader('tokenizers/punkt/english.pickle')
port_sent_tokenizer = LazyLoader('tokenizers/punkt/portuguese.pickle')

log = make_log(__name__)

def tag_collection(args, vent=None):
    """
    POS tag an entire colection of texts on a database
    """
    conn = Connection(host=args.host,port=args.port)
    coll = conn[args.db][args.collection]
    i = 1
    cursor = coll.find({'tagged_text':None},fields=args.fields)
    rd = cursor.count()
    log.info("%s documents need tagging"%rd)
    msgs = []
    for t in cursor:
        log.info("updating %s of %s"%(i,rd))
        lang = 'en' if 'lang' not in t else t['lang']
        msgs.append({'database':args.db,'collection':args.collection,'text':t['text'],'lang':lang,'_id':str(t['_id'])})
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

def main(args):
    """
    Starts the app.
    :param args: args from Argparser passed from pyplncli
    :return:
    """
    tv = TaskVentilator(Ventilator,POSTaggerWorker,MongoUpdateSink,10)
    vent, ws, sink = tv.spawn()
    tag_collection(args, vent)

