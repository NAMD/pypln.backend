#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
Part-of-speech tagger based on NLTK
"""
__docformat__ = "restructuredtext en"

from nltk import pos_tag, word_tokenize
from nltk.data import LazyLoader
from nltk.tag import tuple2str
from pymongo import Connection
from pypln.workers.tagger_worker import POSTaggerWorker
from pypln.sinks.mongo_update_sink import MongoUpdateSink
from pypln.servers.ventilator import Ventilator
from pypln.servers.baseapp import TaskVentilator


taggers = {
           'en': LazyLoader('tokenizers/punkt/english.pickle'),
           'pt': LazyLoader('tokenizers/punkt/portuguese.pickle'),
}

def tag_collection(args, vent=None):
    """ POS tag an entire collection of texts on a database """
    #TODO: get configuration from another place
    conn = Connection(host=args.host, port=args.port)
    coll = conn[args.db][args.collection]
    cursor = coll.find({'tagged_text': None}, fields=args.fields)
    #TODO: use new document-schema
    msgs = []
    for t in cursor:
        lang = 'en' if 'lang' not in t else t['lang']
        msgs.append({'database': args.db, 'collection': args.collection,
                     'text': t['text'], 'lang': lang,'_id': str(t['_id'])})
    if msgs:
        vent.push_load(msgs)

def tag_text(text, lang='en'):
    """ Receive raw text and return tagged text in the format word/tag """
    #TODO: should use ['analysis']['tokens'] instead of tokenizing text
    sents = taggers[lang].tokenize(text)
    tokens = []
    for s in sents:
        tokens.extend(pos_tag(word_tokenize(s)))
    return ' '.join([tuple2str(t) for t in tokens])

def main(args):
    """
    Starts the app.
    :param args: args from Argparser passed from pyplncli
    """
    tv = TaskVentilator(Ventilator, POSTaggerWorker, MongoUpdateSink, 10)
    vent, ws, sink = tv.spawn()
    tag_collection(args, vent)
