#-*- coding:utf-8 -*-
"""
Created on 23/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

import zmq
from base import PushPullWorker
from nltk import ConditionalFreqDist, FreqDist, word_tokenize
from nltk.data import LazyLoader
from collections import OrderedDict


class FreqDistWorker(PushPullWorker):
    def process(self,msg):
        lang = 'en' if 'lang' not in msg else msg['lang']
        fd = FreqDist(word_tokenize(msg['text']))#.encode('utf8')))
        di = OrderedDict(fd).items()
        msgout = {"database" : msg['database'],
                  "collection" : msg['collection'],
                  "spec":{'_id' : msg['_id']},
                  "update" : {'$set':{"freqdist":di}},
                  "multi" : False
        }
        self.sender.send_json(msgout)
        return msgout
