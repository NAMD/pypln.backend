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
from pypln.logger import make_log
from pypln.workers.frequency_worker import FreqDistWorker
from pypln.servers.ventilator import Ventilator
from pypln.servers.baseapp import TaskVentilator
from pypln.sinks.mongo_update_sink import MongoUpdateSink
from bson import BSON
from bson.son import SON

log = make_log(__name__)

#tokenizer = {'en':LazyLoader('tokenizers/punkt/english.pickle'),
#             'pt':LazyLoader('tokenizers/punkt/portuguese.pickle')}

#TODO: implement the possibility to run as a single process or to call workers to do the work in parallel

def frequency(args, vent):
    """
    Calculate frequency distribution (dictionary) of words of each document of the collection and store it
    as a list of items.

    """
    conn = Connection(host=args.host,port=args.port)
    coll = conn[args.db][args.col]
    i = 1
    if args.incr:
        cursor = coll.find({"freqdist":None},fields=[args.field]+['lang'])
    else:
        cursor = coll.find(fields=[args.field]+['lang'])
    rd = cursor.count()
    log.info("{0} documents queued for term frequency analysis.".format(rd))
    msgload = []
    for t in cursor:
        msg = {'database' : args.db,
               'collection' : args.col,
               'text':t[args.field],
               '_id':str(t['_id'])
               }
        msgload.append(msg)
        if len(msgload) == 50:
            vent.push_load(msgload)
            msgload = []
    if msgload:
        vent.push_load(msgload)
    log.info("Done pushing frequency analysis jobs.")

def main(args):
    tv = TaskVentilator(Ventilator,FreqDistWorker,MongoUpdateSink,10)
    vent = tv.spawn()[0]
    frequency(args, vent)


