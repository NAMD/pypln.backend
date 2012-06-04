#-*- coding:utf-8 -*-
"""
Calcuate frequency distribution of words in a text
"""

from pymongo import Connection
from pypln.workers.frequency_worker import FreqDistWorker
from pypln.servers.ventilator import Ventilator
from pypln.servers.baseapp import TaskVentilator
from pypln.sinks.mongo_update_sink import MongoUpdateSink


def frequency(args, vent):
    """
    Calculate frequency distribution of words of each document in a collection
    """
    #TODO: use new document-schema, where freqdist will be available at:
    #      document['analysis']['freqdist']
    #TODO: get configuration from another place
    conn = Connection(host=args.host, port=args.port)
    coll = conn[args.db][args.col]
    i = 1
    if args.incr:
        cursor = coll.find({"freqdist": None}, fields=[args.field] + ['lang'])
    else:
        cursor = coll.find(fields=[args.field] + ['lang'])
    rd = cursor.count()
    msgload = []
    for t in cursor:
        msg = {'database': args.db, 'collection': args.col,
               'text': t[args.field], '_id': str(t['_id'])}
        msgload.append(msg)
        if len(msgload) == 50:
            vent.push_load(msgload)
            msgload = []
    if msgload:
        vent.push_load(msgload)

def main(args):
    tv = TaskVentilator(Ventilator, FreqDistWorker, MongoUpdateSink, 10)
    vent = tv.spawn()[0]
    frequency(args, vent)
